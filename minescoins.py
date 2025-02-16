import smartpy as sp

@sp.module
def main():
    class MinesCoin(sp.Contract):
        def __init__(self, admin):
            self.data.balances = sp.big_map()
            self.data.administrator = admin
            self.data.totalSupply = 0

        @sp.entrypoint
        def transfer(self, origin, destination, amount):
            assert((origin == sp.sender) or
                      (self.data.balances[origin].approvals[sp.sender] >= amount))
            self.addAddressIfNecessary(destination)
            assert(self.data.balances[origin].balance >= amount)
            self.data.balances[origin].balance -= amount
            self.data.balances[destination].balance += amount
            if (origin != sp.sender):
                self.data.balances[origin].approvals[sp.sender] -= amount

        @sp.entrypoint
        def approve(self, destination, amount):
            alreadyApproved = self.data.balances[sp.sender].approvals.get(destination, default=0)
            assert((alreadyApproved == 0) or (amount == 0))
            self.data.balances[sp.sender].approvals[destination] = amount

        @sp.entrypoint
        def mint(self, address, amount):
            assert(sp.sender == self.data.administrator)
            self.addAddressIfNecessary(address)
            self.data.balances[address].balance += amount
            self.data.totalSupply += amount

        @sp.entrypoint
        def burn(self, address, amount):
            assert(sp.sender == self.data.administrator)
            self.addAddressIfNecessary(address)
            assert(self.data.balances[address].balance >= amount)
            self.data.balances[address].balance -= amount
            self.data.totalSupply -= amount

        @sp.private(with_storage="read-write")
        def addAddressIfNecessary(self, address):
            if not(self.data.balances.contains(address)):
                self.data.balances[address] = sp.record(balance = 0, approvals = {})

@sp.add_test()
def test():

    # Create test accounts
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    charlie = sp.test_account("Charlie")

    scenario = sp.test_scenario("MinesCoin", main)
    scenario.h1("Simple FA12 Contract")

    scenario.h2("4.1 Test Accounts")
    # sp.test_account generates ED25519 key-pairs deterministically:
    admin = sp.test_account("Administrator")

    # Let's display the accounts:
    scenario.show([admin, alice, bob, charlie])

    c1 = main.MinesCoin(admin.address)

    scenario += c1

    scenario.h2("4.2 Minting coins")
    scenario.h3("Admin mints 18 coins for Alice")
    c1.mint(address = alice.address, amount = 18, _sender = admin)
    scenario.h3("Admin mints 24 coins for Bob")
    c1.mint(address = bob.address, amount = 24, _sender = admin)
    # We check total supply is 42
    scenario.verify(c1.data.totalSupply == 42)

    scenario.h2("4.3 Transfers and approvals")
    
    scenario.h3("Alice transfers directly 4 tokens to Bob")
    c1.transfer(origin=alice.address, destination=bob.address, amount=4, _sender=alice)
    
    scenario.h3("Charlie tries to transfer from Alice but does not have her approval")
    c1.transfer(origin=alice.address, destination=bob.address, amount=4, _sender=charlie, _valid=False)
        
    scenario.h3("Alice approves Charlie")
    c1.approve(amount=10, destination=charlie.address, _sender=alice)
    
    scenario.h3("Charlie transfers Alice's tokens to Bob")
    c1.transfer(origin=alice.address, destination=bob.address, amount=4, _sender=charlie)
    
    scenario.h3("Charlie tries to over transfer from Alice")
    c1.transfer(origin=alice.address, destination=bob.address, amount=40, _sender=charlie, _valid=False)
        
    scenario.h3("Alice removes the approval for Charlie")
    c1.approve(amount=0, destination=charlie.address, _sender=alice)
    
    scenario.h3("Charlie tries to transfer Alice's tokens to Bob and fails")
    c1.transfer(origin=alice.address, destination=bob.address, amount=4, _sender=charlie, _valid=False)

    scenario.h2("4.4 Burning coins")
    
    scenario.h3("Admin burns Bob token")
    scenario.verify(c1.data.balances[bob.address].balance == 32)
    c1.burn(address = bob.address, amount = 2, _sender = admin)
    scenario.verify(c1.data.balances[bob.address].balance == 30)
    
    scenario.h3("Alice tries to burn Bob token")
    c1.burn(address = bob.address, amount = 2, _sender = alice, _valid=False)
        
    scenario.h3("Admin tries to burn more tokens than Bob owns")
    c1.burn(address = bob.address, amount = 200, _sender = admin, _valid=False)

    # Creation of a new contract
    scenario.h2("4.5 Deploying it on Ghostnet")
    scenario.h3("Deploying with the right initial storage")
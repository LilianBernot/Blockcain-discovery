import smartpy as sp

@sp.module
def main():
    class PoleContract(sp.Contract):
        def __init__(self):
            self.data.votes = sp.big_map()  
            # Track who voted and for what
            
            self.data.chocolatine_count = 0
            self.data.pain_au_chocolat_count = 0
            self.data.vote_price = sp.tez(5)

        @sp.entrypoint
        def vote(self, choice):
            # TODO : make vote cost 5 tez
            # assert sp.amount == self.data.vote_price, "You must send exactly 5 tez to vote."
            assert not self.data.votes.contains(sp.sender), "You have already voted."

            assert choice == "chocolatine" or choice == "pain_au_chocolat", "bad choice"
            
            if choice == "chocolatine":
                self.data.chocolatine_count += 1
                self.data.votes[sp.sender] = choice
            if choice == "pain_au_chocolat":
                self.data.pain_au_chocolat_count += 1
                self.data.votes[sp.sender] = choice

@sp.add_test()
def test():
    scenario_name = "Pole test"
    scenario = sp.test_scenario(scenario_name, main)
    scenario.h1(scenario_name)
    
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    charlie = sp.test_account("Charlie")
    
    contract = main.PoleContract()
    scenario += contract
    
    # Alice votes for chocolatine
    contract.vote("chocolatine", _sender=alice)
    scenario.verify(contract.data.chocolatine_count == 1)
    
    # Bob votes for pain au chocolat
    contract.vote("pain_au_chocolat", _sender=bob)
    scenario.verify(contract.data.pain_au_chocolat_count == 1)
    
    # Alice tries to vote again (should fail)
    contract.vote("pain_au_chocolat", _sender=alice, _valid=False)
    
    # Bob tries to vote without sending 5 tez (should fail)
    contract.vote("chocolatine", _sender=bob, _valid=False)
    
    # An invalid choice (should fail)
    contract.vote("baguette", _sender=charlie, _valid=False)

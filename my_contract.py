import smartpy as sp

@sp.module
def main():
    class MyContract(sp.Contract):
        def __init__(self, myParameter):
            sp.cast(myParameter, sp.int)
            self.data.myParameter = myParameter
            self.data.maximum = 42
            self.data.minimum = 0

        @sp.entrypoint
        def increment(self, params):
            assert params > self.data.minimum, "Incrementation should be positive"
            assert self.data.myParameter + params <= self.data.maximum, "Maximum value has been reached"
            assert self.data.myParameter + params > self.data.minimum, "Contract value can't be negative"
            self.data.myParameter += params

        @sp.entrypoint
        def reset(self):
            self.data.myParameter = self.data.minimum

# Tests
@sp.add_test()
def test():
    scenario = sp.test_scenario("Welcome", main)
    scenario.h1("Welcome")

    contract = main.MyContract(12)
    scenario += contract

    contract.increment(12)

    scenario.verify(contract.data.myParameter == 24)

@sp.add_test()
def maximum_test(name="Test failure : maximum value reached"):
    """
    Tests that contract does not accept more than a maximum value.
    """
    scenario = sp.test_scenario(name, main)
    scenario.h1(name)

    contract = main.MyContract(12)
    scenario += contract

    # Action should not be valid
    contract.increment(contract.data.maximum, _valid=False)
    # myParameter should not have been changed
    scenario.verify(contract.data.myParameter == 12)

@sp.add_test()
def negative_incrementation_test(name="Test failure : increment should be positive"):
    """
    Tests that contract does not accept negative incrementation.
    """
    scenario = sp.test_scenario(name, main)
    scenario.h1(name)

    contract = main.MyContract(12)
    scenario += contract

    # Action should not be valid
    contract.increment(-50, _valid=False)
    # myParameter should not have been changed
    scenario.verify(contract.data.myParameter == 12)

@sp.add_test()
def maximum_blocks_and_reset_test(name="Test maximum : when contract is at maximum, it is blocked"):
    """
    Tests that when contract is at maximum, it is blocked.
    It also test the reset function.
    """
    scenario = sp.test_scenario(name, main)
    scenario.h1(name)

    contract = main.MyContract(0)
    scenario += contract

    # Make contract to its maximum
    contract.increment(contract.data.maximum)

    # Add negative value : action should not be valid
    contract.increment(-50, _valid=False)
    scenario.verify(contract.data.myParameter == contract.data.maximum)

    # Add 0 : action should not be valid
    contract.increment(0, _valid=False)
    scenario.verify(contract.data.myParameter == contract.data.maximum)

    # Add some : action should not be valid
    contract.increment(10, _valid=False)
    scenario.verify(contract.data.myParameter == contract.data.maximum)

    contract.reset()
    scenario.verify(contract.data.myParameter == 0)

    # Contrat is rest, we can increment it
    contract.increment(12)
    scenario.verify(contract.data.myParameter == 12)
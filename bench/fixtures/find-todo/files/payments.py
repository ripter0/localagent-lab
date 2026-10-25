def charge(account, amount):
    """Take money from an account."""
    # TODO: handle negative amounts (right now they add money to the account)
    account["balance"] -= amount
    return account

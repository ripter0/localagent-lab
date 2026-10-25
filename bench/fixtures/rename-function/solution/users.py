USERS = {1: "anna", 2: "luca", 3: "sara"}


def get_user(user_id):
    """Return the user name for an id, or 'unknown'."""
    return USERS.get(user_id, "unknown")

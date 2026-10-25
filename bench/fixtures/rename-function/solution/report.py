import users


def user_line(user_id):
    return f"#{user_id}: {users.get_user(user_id)}"

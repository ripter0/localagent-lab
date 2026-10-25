import users


def user_line(user_id):
    return f"#{user_id}: {users.get_usr(user_id)}"

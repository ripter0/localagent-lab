from users import get_user


def handle_request(user_id):
    return {"user": get_user(user_id)}

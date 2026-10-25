from users import get_usr


def handle_request(user_id):
    return {"user": get_usr(user_id)}

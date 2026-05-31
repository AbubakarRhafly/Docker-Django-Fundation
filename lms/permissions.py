def get_role(user):
    if hasattr(user, "profile"):
        return user.profile.role
    return None


def is_admin(user):
    return get_role(user) == "admin"


def is_instructor(user):
    return get_role(user) == "instructor"


def is_student(user):
    return get_role(user) == "student"
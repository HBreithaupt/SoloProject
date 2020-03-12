import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

def email_verify(email):
    if not EMAIL_REGEX.match(email):
        return False

    return True

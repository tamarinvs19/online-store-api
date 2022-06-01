from random import choices
import string


def generate_token(size: int = 127) -> str:
    characters = (
        string.ascii_letters
        + string.digits
        + '-._~'
    )
    return ''.join(choices(characters, k=size))


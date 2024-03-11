from app import turnstile

def has_failed_turnstile() -> bool:
    if not turnstile.verify():
        flash("you are a bot aren't you")
        return True
    return False

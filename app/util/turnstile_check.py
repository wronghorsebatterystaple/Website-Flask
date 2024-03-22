from app import turnstile

# Check Cloudflare Turnstile captcha (apparently separate file works?)
def has_failed_turnstile() -> bool:
    if not turnstile.verify():
        flash("you are a bot aren't you")
        return True
    return False

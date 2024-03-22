from urllib.parse import quote

# Designed to mimic JavaScript's encodeURIComponent(), based off StackOverflow
def encode_uri_component(s: str) -> str:
    return quote(s, safe="~!*()'")

# Concat flash message to URL as query string, without url_for()
def url_with_flash(URL:str, flash: str) -> str:
    return f"{URL}?flash={flash}"

from urllib.parse import quote

# Designed to mimic JavaScript's encodeURIComponent(), from StackOverflow
def encode_uri_component(s: str) -> str:
    return quote(s, safe="~!*()'")

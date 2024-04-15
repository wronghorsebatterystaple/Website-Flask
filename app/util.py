from urllib.parse import quote

# Designed to mimic JavaScript's encodeURIComponent(), from StackOverflow
def encode_URI_component(s: str) -> str:
    return quote(s, safe="~!*()'")

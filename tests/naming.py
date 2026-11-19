import re


def slug(text: str) -> str:
    return re.sub(r"[^\w-]+", "-", text).strip("-")

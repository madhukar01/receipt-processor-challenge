import functools


def sanitize_text(text: str) -> str:
    """
    Sanitize text to a valid file name.

    Args:
        text: Text to sanitize

    Returns:
        str: Sanitized text

    Raises:
        ValueError: If text is invalid
    """
    if not text.strip():
        raise ValueError("Invalid text")

    chars_to_replace = [" ", "-", ".", ":", "(", ")", "/", "\\"]
    sanitized = functools.reduce(
        lambda n, char: n.replace(char, "_"),
        chars_to_replace,
        text.strip().lower(),
    )

    # Replace multiple consecutive underscores with a single underscore
    return "_".join(filter(None, sanitized.split("_")))

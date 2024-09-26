import os


def dprint(message):
    """
    Prints a debug message if the DEBUG flag is set.
    """
    DEBUG = os.getenv("DEBUG_APP")
    if DEBUG:
        print(f"[DEBUG] {message}")

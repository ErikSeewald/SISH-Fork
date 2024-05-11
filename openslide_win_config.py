"""
Unfortunately, the multiprocessing module gets weird with dynamically created globals, so statically modifying this
file seems to be the best option for windows users...
"""


def get_openslide_path() -> str:
    return "C:/Users/Erik/openslide-win64/bin"

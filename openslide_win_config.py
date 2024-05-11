"""
Unfortunately, the multiprocessing module gets weird with dynamically created globals, so statically modifying this
file seems to be the best option for windows users...
"""


def get_openslide_path() -> str:
    print("Loading openslide path from openslide_win_config.py. If you are on windows, you need to modify"
          " this file yourself and replace the returned path with your own path to /openslide-win64/bin.")
    return "C:/Users/Erik/openslide-win64/bin"

'''
Author: Quinn (Gigawttz)

What it Does: Creates the spotify client Obj that is then referenced
and passed through later spotify API methods
'''

from .spotify_client import get_spotify_client  # type: ignore


def main():
    sp = get_spotify_client()




if __name__ == '__main__':
    sp = get_spotify_client()

import sys


def is_testing_mode():
    return sys.argv[1] == 'test'

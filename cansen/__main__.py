import sys

from .cansen import cansen


def main(args=None):
    if args is None:
        args = sys.argv[1:]
        cansen(args)


if __name__ == '__main__':
    sys.exit(main())

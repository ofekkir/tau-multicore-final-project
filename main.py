#!/usr/bin/python
import sys
import traceback


def main():
    try:

        return 0
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
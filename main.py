#!/usr/bin/python3
import sys
import traceback

from sam import Sam
import config

def main():
    try:
        sam = Sam()
        sam.run()
        return 0
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
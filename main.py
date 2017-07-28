#!/usr/bin/python3
import sys
import traceback

from sam import Sam
import config

def main():
    try:
        config.NUMBER_OF_ITERATIONS = int(sys.argv[1])
        sam = Sam()
        sam.run()
        return 0
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage me <number of iterations> (-1 means forever)')
        sys.exit(1)
    sys.exit(main())
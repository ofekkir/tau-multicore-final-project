import sys
import subprocess
import time
import random
import os

def test():
    tmpdir = '/tmp/linux_kernel_{}/'.format(random.randint(0, 100))
    subprocess.check_call('cp -r {} {}'.format('/home/ofekkirzner/sam/linux-4.4.0', tmpdir).split())

    start_no_sam = time.time()
    # p = subprocess.Popen('make -j'.split(), cwd=tmpdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p = subprocess.Popen('rm -rf {}'.format(tmpdir).split(), cwd=tmpdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p.wait()

    end_no_sam = time.time()

    # os.rmdir(tmpdir)

    return end_no_sam - start_no_sam

def main():
    print(test())


if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/python

import sys

def main():
    if (len(sys.argv) < 3):
        sys.exit(0)
    core1_str = "cpu=" + sys.argv[2]
    core2_str = "cpu=" + sys.argv[3]
    f = open(sys.argv[1], 'r')
    content = f.readlines()
    lines = [ x for x in content if (core1_str in x  or core2_str in x)]
    lines = [w.replace('Measurements(', '') for w in lines]
    lines = [w.replace('),\n', '') for w in lines]
    all_meas = [ l.split(", ") for l in lines]
    line_length = len(lines[0].split(", "))
    total_lines = len(lines)
    for i in range(line_length):
        meas_name = all_meas[0][i].split("=")[0]
        meas_sum = 0
        for l in all_meas:
            meas_sum = meas_sum + int(l[i].split("=")[1])
        meas_avg = meas_sum / total_lines
        print meas_name + " avg : " + str(meas_avg) 
# display some lines

if __name__ == "__main__": main()

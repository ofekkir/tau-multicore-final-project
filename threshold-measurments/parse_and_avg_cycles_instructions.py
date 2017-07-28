#!/usr/bin/python

import sys

def main():
    if (len(sys.argv) < 1):
        sys.exit(0)
#    core1_str = "cpu=" + sys.argv[2]
#    core2_str = "cpu=" + sys.argv[3]
    f = open(sys.argv[1], 'r')
    content = f.readlines()
    lines = content
#    lines = [ x for x in content if (core1_str in x  or core2_str in x)]
    lines = [w.replace('Measurements(', '') for w in lines]
    lines = [w.replace('),\n', '') for w in lines]
    lines = [w.replace(')]\n', '') for w in lines]
    all_meas = [ l.split(", ") for l in lines]
    line_length = len(lines[0].split(", "))
    total_lines = len(lines)
    print "length = " + str(total_lines)
    for i in range(line_length):
        meas_name = all_meas[0][i].split("=")[0]
        meas_sum = 0
        for l in all_meas:
            meas_sum = meas_sum + int(l[i].split("=")[1])
        meas_avg = meas_sum / total_lines
        if("instructions" == meas_name):
            instructions_avg = meas_avg
            dev_sum = 0
            for l in all_meas:
                print "instructions = " + str(int(l[i].split("=")[1])) + " avg = " + str(instructions_avg) + " dev = " + str(abs(int(l[i].split("=")[1]) - instructions_avg))
                dev_sum = dev_sum + abs(int(l[i].split("=")[1]) - instructions_avg)
            print "instructions avg = " + str(instructions_avg) + " dev = " + str(dev_sum / total_lines)
        if("cycles" == meas_name):
            cycles_avg = meas_avg
            dev_sum = 0
            for l in all_meas:
                dev_sum = dev_sum + abs(int(l[i].split("=")[1]) - cycles_avg)
            print "cycles avg = " + str(cycles_avg) + " dev = " + str(dev_sum / total_lines)
        print meas_name + " sum : " + str(meas_sum)
 
# display some lines

if __name__ == "__main__": main()

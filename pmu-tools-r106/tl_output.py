# Copyright (c) 2012-2015, Intel Corporation
# Author: Andi Kleen
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# Output toplev results in various formats

import locale
import csv
import re
from tl_stat import format_valstat, combine_valstat, isnan

class Output:
    """Abstract base class for Output classes."""
    def __init__(self, logfile, version):
        self.logf = logfile
        self.printed_descs = set()
        self.hdrlen = 30
        self.version = version

    # pass all possible hdrs in advance to compute suitable padding
    def set_hdr(self, hdr, area):
        if area:
            hdr = "%-7s %s" % (area, hdr)
        self.hdrlen = max(len(hdr) + 1, self.hdrlen)

    def set_cpus(self, cpus):
	pass

    def item(self, area, name, l, timestamp, remark, desc, title, sample, valstat):
        if desc in self.printed_descs:
            desc = ""
        else:
            self.printed_descs.add(desc)
        if not area:
            area = ""
        self.show(timestamp, title, area, name, l, remark, desc, sample, valstat)

    def ratio(self, area, name, l, timestamp, remark, desc, title, sample, valstat):
        self.item(area, name, "%13.2f" % (100.0 * l), timestamp, "%" + remark, desc, title,
                  sample, valstat)

    def metric(self, area, name, l, timestamp, desc, title, unit, valstat):
        self.item(area, name, "%13.2f" % l, timestamp, unit, desc, title,
                  None, valstat)

    def flush(self):
	pass

    def bottleneck(self, key, name, val):
	pass

class OutputHuman(Output):
    """Generate human readable single-column output."""
    def __init__(self, logfile, args, version):
        Output.__init__(self, logfile, version)
        locale.setlocale(locale.LC_ALL, '')
        self.args = args
	self.titlelen = 7

    def set_cpus(self, cpus):
        self.titlelen = max(map(len, cpus)) + 1

    def print_desc(self, desc, sample):
	if desc and not self.args.no_desc:
	    print >>self.logf, "\t" + desc
	if desc and sample and not self.args.no_desc:
	    print >>self.logf, "\t" + "Sampling events: ", sample

    def print_timestamp(self, timestamp):
	if timestamp:
	    self.logf.write("%6.9f%s" % (timestamp, " "))

    def print_header(self, area, hdr):
	hdr = "%-7s %s" % (area, hdr)
	self.logf.write("%-*s " % (self.hdrlen, hdr + ":"))

    # timestamp Timestamp in interval mode
    # title     CPU
    # area      FE/BE ...
    # hdr       Node Name
    # s         Formatted measured value
    # remark    above/below/""
    # desc      Object description
    # sample    Sample Objects (string)
    # vs        Statistics object
    # Example:
    # C0    BE      Backend_Bound:                                62.00 %
    def show(self, timestamp, title, area, hdr, s, remark, desc, sample, valstat):
	self.print_timestamp(timestamp)
        write = self.logf.write
        if title:
            write("%-*s" % (self.titlelen, title))
        vs = format_valstat(valstat)
	self.print_header(area, hdr)
        if vs:
            val = "%-25s %s" % (s + " " + remark, vs)
        else:
            val = "%s %s" % (s, remark)
        write(val + "\n")
	self.print_desc(desc, sample)

    def metric(self, area, name, l, timestamp, desc, title, unit, valstat):
        if l > 1000:
            val = locale.format("%13u", round(l), grouping=True)
        else:
            val = "%13.2f" % (l)
        self.item(area, name, val, timestamp, unit, desc, title,
                  None, valstat)

    def bottleneck(self, key, name, val):
	if key:
	    key += " "
	print >>self.logf, "%sBOTTLENECK %s %.2f%%" % (key, name, val * 100.)

class OutputColumns(OutputHuman):
    """Human-readable output data in per-cpu columns."""
    def __init__(self, logfile, args, version):
	OutputHuman.__init__(self, logfile, args, version)
	self.nodes = dict()
	self.timestamp = None
	self.cpunames = set()
        self.printed_header = False

    def set_cpus(self, cpus):
	self.cpunames = cpus

    def show(self, timestamp, title, area, hdr, s, remark, desc, sample, valstat):
        if self.args.single_thread:
            OutputHuman.show(self, timestamp, title, area, hdr, s, remark, desc, sample, valstat)
            return
	self.timestamp = timestamp
	key = (area, hdr)
	if key not in self.nodes:
	    self.nodes[key] = dict()
	assert title not in self.nodes[key]
	self.nodes[key][title] = (s, remark, desc, sample, valstat)

    def flush(self):
	VALCOL_LEN = 14
	write = self.logf.write

	cpunames = sorted(self.cpunames)

        if not self.printed_header:
	    if self.timestamp:
	        write("%9s" % "")
	    write("%*s" % (self.hdrlen, ""))
	    for j in cpunames:
	        write("%*s " % (VALCOL_LEN, j))
	    write("\n")
            self.printed_header = True

        for key in sorted(sorted(self.nodes.keys(), key=lambda x: x[1]), key=lambda x: x[0] == ""):
	    node = self.nodes[key]
	    desc = None
	    sample = None
            remark = None
	    if self.timestamp:
		self.print_timestamp(self.timestamp)

	    self.print_header(key[0], key[1])
            vlist = []
	    for cpuname in cpunames:
		if cpuname in node:
		    cpu = node[cpuname]
		    desc, sample, remark, valstat = cpu[2], cpu[3], cpu[1], cpu[4]
                    if remark in ("above", "below", "Metric", "CoreMetric", "CoreClocks"): # XXX
                        remark = ""
                    if valstat:
                        vlist.append(valstat)
		    write("%*s " % (VALCOL_LEN, cpu[0]))
		else:
		    write("%*s " % (VALCOL_LEN, ""))
            if remark:
                vs = format_valstat(combine_valstat(vlist))
                write(" %-5s %s" % (remark, vs))
	    write("\n")
	    self.print_desc(desc, sample)
	self.nodes = dict()

class OutputColumnsCSV(OutputColumns):
    """Columns output in CSV mode."""

    def __init__(self, logfile, sep, args, version, cpu):
        OutputColumns.__init__(self, logfile, args, version)
        self.writer = csv.writer(self.logf, delimiter=sep)
        self.printed_header = False
        self.writer.writerow(["# " + version + " on " + cpu.name])

    def show(self, timestamp, title, area, hdr, s, remark, desc, sample, valstat):
	self.timestamp = timestamp
	key = (area, hdr)
	if key not in self.nodes:
	    self.nodes[key] = dict()
	assert title not in self.nodes[key]
	self.nodes[key][title] = (s, remark, desc, sample, valstat)

    def flush(self):
        cpunames = sorted(self.cpunames)
        if not self.printed_header:
            ts = ["Timestamp"] if self.timestamp else []
            self.writer.writerow(ts + ["Area", "Node"] + cpunames + ["Description", "Sample", "Stddev", "Multiplex"])
            self.printed_header = True
        for key in sorted(sorted(self.nodes.keys(), key=lambda x: x[1]), key=lambda x: x[0] == ""):
	    node = self.nodes[key]
            ts = [self.timestamp] if self.timestamp else []
            l = ts + [key[0], key[1]]
            vlist = []
            ol = dict()
            desc, sample = "", ""
            for cpuname in cpunames:
                if cpuname in node:
		    cpu = node[cpuname]
                    if cpu[2]:
                        desc = cpu[2]
                        desc = re.sub(r"\s+", " ", desc)
                    if cpu[3]:
                        sample = cpu[3]
                    # ignore remark for now
                    if cpu[4]:
                        vlist.append(cpu[4])
                    ol[cpuname] = float(cpu[0])
            l += [ol[x] if x in ol else "" for x in cpunames]
            l.append(desc)
            l.append(sample)
            vs = combine_valstat(vlist)
            if vs:
                l += (vs.stddev, vs.multiplex if not isnan(vs.multiplex) else "")
            else:
                l += ["", ""]
            self.writer.writerow(l)
        self.nodes = dict()

class OutputCSV(Output):
    """Output data in CSV format."""
    def __init__(self, logfile, sep, args, version, cpu):
        Output.__init__(self, logfile, version)
        self.writer = csv.writer(self.logf, delimiter=sep)
        self.args = args
        self.writer.writerow(["# " + version + " on " + cpu.name])

    def show(self, timestamp, title, area, hdr, s, remark, desc, sample, valstat):
        if self.args.no_desc:
            desc = ""
        desc = re.sub(r"\s+", " ", desc)
        l = []
        if timestamp:
            l.append(timestamp)
        if title:
            l.append(title)
        stddev = valstat.stddev if (valstat and valstat.stddev) else ""
        multiplex = valstat.multiplex if (valstat and valstat.multiplex == valstat.multiplex) else ""
        self.writer.writerow(l + [hdr, s.strip(), remark, desc, sample, stddev, multiplex])

    def bottleneck(self, key, name, val):
        self.writer.writerow((key, "BOTTLENECK", name, val * 100.))

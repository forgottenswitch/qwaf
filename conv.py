import os
import sys
import shlex

import conv.xkb

def usage():
    print("Usage: conv.py [-o OUTPUT_DIR] INPUT_FILE")
    print(" Custom keyboard layout compiler")

outdir = "gen"

in_arg, tail = None, []
for arg in sys.argv:
    if in_arg == "-o":
        outdir = arg
        in_arg = None
    else:
        if arg[:1] == "-":
            if arg in ["-o"]:
                in_arg = arg
            else:
                usage()
                sys.exit(1)
        tail.append(arg)

if len(tail) < 1:
    usage()
    sys.exit(1)

infile = tail[0]

def fatal(msg):
    print(msg)
    sys.exit(1)

if not os.path.exists(infile):
    fatal("INPUT_FILE must exist")

indir = os.path.dirname(infile)

layouts = []
partials = []

def read_file(filename, as_partials=False):
    with open(filename, "r") as f:
        lines = f.readlines()
    for nl, l in enumerate(lines, 1):
        toks = shlex.split(l)
        print(str(toks))

read_file("layouts")

if not os.path.exists(outdir):
    os.mkdir(outdir)

for outm in [conv.xkb]:
    outmdir = os.path.join(outdir, outm.name)
    print([":", outmdir])
    if not os.path.exists(outmdir):
        os.mkdir(outmdir)
    outm.convert(outdir)

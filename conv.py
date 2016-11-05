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

class Keydefs:
    def __init__(self, filename, name):
        self.filename = filename
        self.name = name
        self.includes = []
        self.keys = []

    def __str__(self):
        return """Keydefs< '{}({})' {}\n {}>""".format(
                self.filename, self.name,
                self.includes, self.keys)

def read_file(filename, as_partials=False):
    filename_name = os.path.basename(filename)

    def syntax_error(msg):
        nonlocal filename, nl
        fatal("{}:{}: {}".format(filename, nl, msg))

    def check_for_cur_defs():
        nonlocal filename, nl, cur_defs
        if not cur_defs:
            fatal("{}:{}: need to be in 'symbols'".format(filename, nl))

    with open(filename, "r") as f:
        lines = f.readlines()
    cur_defs = None
    for nl, l in enumerate(lines, 1):
        toks = shlex.split(l)
        print(str(toks))
        if len(toks):
            tok, *args = toks
            if tok == '#':
                True
            elif tok == "symbols" and not as_partials:
                if len(args) < 1:
                    syntax_error("expected argument to 'symbols'")
                cur_defs = Keydefs(filename_name, args[0])
                layouts.append(cur_defs)
            elif tok == "include":
                if len(args) < 1:
                    syntax_error("expected argument to 'include'")
                cur_defs.includes.append(args[0])
            else:
                syntax_error("unknown directive '{}'".format(tok))

read_file("layouts")
for l in layouts:
    print(l)
exit()

if not os.path.exists(outdir):
    os.mkdir(outdir)

for outm in [conv.xkb]:
    outmdir = os.path.join(outdir, outm.name)
    print([":", outmdir])
    if not os.path.exists(outmdir):
        os.mkdir(outmdir)
    outm.convert(outdir)

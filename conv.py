import os
import sys
import shlex
import re
import pprint

import conv.xkb

def usage():
    print("Usage: conv.py [-o OUTPUT_DIR] INPUT_FILE")
    print(" Custom keyboard layout compiler")


def split_further(ary, sep_re):
    ret = []
    for x in ary:
        ret += re.split(sep_re, str(x))
    return ret

def remove_matches_in_list(ary, regex):
    ret = []
    for x in ary:
        y = re.sub(regex, "", str(x))
        if y:
            ret.append(y)
    return ret

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
        keys = ""
        for k in self.keys:
            keys += "    {}\n".format(k)
        return """Keydefs<{} ({}) includes={}\n  keys=[\n{}  ]>""".format(
                repr(self.filename),
                repr(self.name),
                self.includes,
                keys)

    def __repr__(self):
        return self.__str__()

COMMA_RE = re.compile(r"[ \t]*,[ \t]*")
COLON_COMMA_RE = re.compile(r"[ \t]*[,:][ \t]*")
MAX_LEVELS = 8

def read_file(filename, as_partials=False):
    print("Reading {}".format(filename))
    filename_name = os.path.basename(filename)

    def syntax_error(msg):
        nonlocal filename, nl
        fatal("{}:{}: {}".format(filename, nl, msg))

    def expect_argc(n):
        nonlocal args
        if len(args) < n:
            if n == 1:
                syntax_error("expected an argument")
            else:
                syntax_error("expected {} arguments".format(n))

    def split_args_by_commas():
        nonlocal args
        args = split_further(args, COMMA_RE)
        print("  {}".format(repr(args)))

    def remove_colons_and_commas_in_args():
        nonlocal args
        args = remove_matches_in_list(args, COLON_COMMA_RE)
        print("  {}".format(repr(args)))

    def check_for_cur_defs():
        nonlocal filename, nl, cur_defs
        if not cur_defs:
            fatal("{}:{}: need to be in 'symbols'".format(filename, nl))

    with open(filename, "r") as f:
        lines = f.readlines()
    cur_defs = None
    cur_levels = [1]
    for nl, l in enumerate(lines, 1):
        toks = shlex.split(l)
        print(str(toks))
        if len(toks):
            tok, *args = toks
            if tok == '#':
                True
            elif tok == "symbols":
                expect_argc(1)
                cur_defs = Keydefs(filename_name, args[0])
                if as_partials:
                    partials.append(cur_defs)
                else:
                    layouts.append(cur_defs)
            elif tok == "include":
                expect_argc(1)
                indir_file = os.path.join(indir, args[0])
                cur_defs.includes.append(args[0])
                if os.path.exists(indir_file):
                    read_file(indir_file, True)
            elif tok == "keytype":
                expect_argc(1)
                cur_defs.keys.append(["keytype", args[0]])
            elif tok == "levels":
                split_args_by_commas()
                expect_argc(1)
                cur_levels = []
                for arg in args:
                    try:
                        x = int(arg)
                    except Exception as e:
                        syntax_error("expected integer (got '{}')".format(arg))
                    if x < 1 or x > MAX_LEVELS:
                        syntax_error("expected integer in [1;{}] (got '{}')".format(MAX_LEVELS, arg))
                    cur_levels.append(x)
            elif tok == "key" or tok == "replace_key":
                remove_colons_and_commas_in_args()
                expect_argc(1 + len(cur_levels))
                kcode, *args = args
                ksyms = [None] * MAX_LEVELS
                for i, lv in enumerate(cur_levels):
                    keysym = args[i]
                    ksyms[lv-1] = keysym
                cur_defs.keys.append([tok, kcode, ksyms])
            elif tok == "modifier_key":
                if len(args) != 2:
                    syntax_error("expected a single argument (got {})".format(repr(args[1:])))
                kcode, *args = args
                cur_defs.keys.append([tok, kcode, args[0]])
            else:
                syntax_error("unknown directive '{}'".format(tok))

read_file("layouts")
print("\nLayouts =============")
pprint.pprint(layouts)
print("\nPartials ============")
pprint.pprint(partials)
exit()

if not os.path.exists(outdir):
    os.mkdir(outdir)

for outm in [conv.xkb]:
    outmdir = os.path.join(outdir, outm.name)
    print([":", outmdir])
    if not os.path.exists(outmdir):
        os.mkdir(outmdir)
    outm.convert(outdir)

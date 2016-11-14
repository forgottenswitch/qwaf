import os
import sys
import shlex
import re
import pprint
import shutil
import copy

import conv.xkb
import conv.svg

def usage():
    print("Usage: conv.py [-o OUTPUT_DIR] [-g] INPUT_FILE")
    print(" Custom keyboard layout compiler")


def split_further(ary, sep_re):
    ret = []
    for x in ary:
        ret += re.split(sep_re, str(x))
    return ret

def remove_matches_in_list(ary, regex):
    ret = []
    for x in ary:
        components = re.split(regex, str(x))
        for y in components:
            if len(y):
                ret.append(y)
    return ret

outdir = "gen"
adddir = "add"
debug = False

in_arg, tail = None, []
for arg in sys.argv:
    if in_arg == "-o":
        outdir = arg
        in_arg = None
    else:
        if arg[:1] == "-":
            if arg in ["-o"]:
                in_arg = arg
            elif arg in ["-g"]:
                debug = True
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

keydefs = {}

SPACE_RE = re.compile(r"[ \t]+")
DEFINE_RE = re.compile(r"^[ \t]*#define[ \t]")

def read_keydefs_file(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    for l in lines:
        if re.match(DEFINE_RE, l):
            components = re.split(SPACE_RE, l)
            symname = components[1][3:]
            symcode = int(components[2], base=16)
            if symcode < 0x100:
                keydefs[symname] = symcode
            if symcode >= 0x01000100 and symcode <= 0x0110ffff:
                utfcode = symcode - 0x01000000
                keydefs[symname] = utfcode

read_keydefs_file("fetch/keysymdef.h")

if debug:
    pprint.pprint(keydefs)

if not os.path.exists(infile):
    fatal("INPUT_FILE must exist")

indir = os.path.dirname(infile)

layouts = []
partials = []

PAREN_RE = re.compile(r"[()]+")

def get_part_by_name(s):
    components = re.split(PAREN_RE, s)
    if len(components) < 2:
        if debug:
            print("Missing partial file name: '{}'".format(s))
        filename = components[0]
        partname = None
    else:
        filename, partname, *_ = components
    for x in (partials + layouts):
        if x.filename == filename:
            if not partname or x.name == partname:
                return x
    if debug:
        print("Missing any symbols in file '{}'".format(filename))


class Keydefs:
    def __init__(self, filename, name):
        self.filename = filename
        self.name = name
        self.includes = []
        self.keys = []
        self.compiled = False
        self.compiled_keys = []

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

    def compile(self):
        if self.compiled:
            return
        print("Compiling '{}({})'".format(self.filename, self.name))
        self.compiled_keys = copy.copy(self.keys)
        for inc in self.includes:
            partial = get_part_by_name(inc)
            if not partial:
                if debug:
                    print("Considering '{}' to be a system partial (cannot find it)".format(inc))
            else:
                partial.compile()
                for key in partial.compiled_keys:
                    merged = False
                    if key[0] == "key":
                        for k1 in self.compiled_keys:
                            if k1[:2] == key[:2]:
                                merged = True
                                for lv, ksym in enumerate(key[2]):
                                    if ksym:
                                        k1[2][lv] = ksym
                    if not merged:
                        self.compiled_keys.append(key)
        self.compiled_keys.sort()
        if debug:
            print("Compiled '{}({})': {}".format(self.filename, self.name, self.compiled_keys))
        self.compiled = True

COMMA_RE = re.compile(r"[ \t]*,[ \t]*")
COLON_COMMA_RE = re.compile(r"[ \t]*[,:][ \t]*")
MAX_LEVELS = 8

files_already_read = []

def read_file(filename, as_partials=False):
    global debug

    print("Reading {}".format(filename))
    filename_name = os.path.basename(filename)

    def syntax_error(msg):
        nonlocal filename, nl, l
        fatal("{}:{}: {}\n  {}".format(filename, nl, msg, l))

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
        if debug: print("  {}".format(repr(args)))

    def remove_colons_and_commas_in_args():
        nonlocal args
        args = remove_matches_in_list(args, COLON_COMMA_RE)
        if debug: print("  {}".format(repr(args)))

    def check_for_cur_defs():
        nonlocal filename, nl, cur_defs
        if not cur_defs:
            fatal("{}:{}: need to be in 'symbols'".format(filename, nl))

    def str_to_xkb_level(arg):
        try:
            x = int(arg)
        except Exception as e:
            syntax_error("expected integer (got '{}')".format(arg))
            if x < 1 or x > MAX_LEVELS:
                syntax_error("expected integer in [1;{}] (got '{}')".format(MAX_LEVELS, arg))
        return x

    with open(filename, "r") as f:
        lines = f.readlines()
    cur_defs = None
    cur_level = 1
    for nl, l in enumerate(lines, 1):
        toks = shlex.split(l)
        if debug: print(str(toks))
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
                inc_arg = args[0]
                inc_filename = re.sub("[(].*", "", inc_arg)
                indir_file = os.path.join(indir, inc_filename)
                cur_defs.includes.append(inc_arg)
                if os.path.exists(indir_file) and inc_filename not in files_already_read:
                    files_already_read.append(inc_filename)
                    read_file(indir_file, True)
            elif tok == "keytype":
                expect_argc(1)
                cur_defs.keys.append(["keytype", args[0]])
            elif tok == "level":
                split_args_by_commas()
                expect_argc(1)
                cur_level = str_to_xkb_level(args[0])
            elif tok == "key" or tok == "replace_key":
                remove_colons_and_commas_in_args()
                kcode, *args = args
                ksyms = [None] * MAX_LEVELS
                if cur_level is not None:
                    for i, keysym in enumerate(args):
                        lv = cur_level + i
                        if lv > MAX_LEVELS:
                            syntax_error("only {} levels are supported".format(MAX_LEVELS))
                        ksyms[lv-1] = keysym
                cur_defs.keys.append([tok, kcode, ksyms])
            elif tok == "modifier_key":
                remove_colons_and_commas_in_args()
                if len(args) != 2:
                    syntax_error("expected a single argument (got {})".format(repr(args[1:])))
                kcode, *args = args
                cur_defs.keys.append([tok, kcode, args[0]])
            else:
                syntax_error("unknown directive '{}'".format(tok))

read_file("layouts")

for x in layouts:
    x.compile()

if debug:
    print("\nLayouts =============")
    pprint.pprint(layouts)
    print("\nPartials ============")
    pprint.pprint(partials)

if not os.path.exists(outdir):
    os.mkdir(outdir)

for outm in [conv.xkb, conv.svg]:
    outmdir = os.path.join(outdir, outm.name)
    addmdir = os.path.join(adddir, outm.name)

    if os.path.exists(addmdir):
        print("Putting additional files from {} to {}".format(addmdir, outmdir))

        def cp_f(src, dst, *, follow_symlinks=True):
            try:
                shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
            except FileExistsError:
                pass

        shutil.copytree(addmdir, outmdir, symlinks=True, ignore_dangling_symlinks=True,
                copy_function=cp_f)

    print("Converting as {} into {}".format(outm.name, outmdir))
    if not os.path.exists(outmdir):
        os.mkdir(outmdir)
    outm.convert(debug, outmdir, keydefs, layouts, partials)


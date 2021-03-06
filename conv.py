import os
import sys
import shlex
import re
import pprint
import shutil
import copy

import conv.xkb
import conv.svg
import conv.linux_console
from conv.utils import int_to_base

conv_to_perform = [
    conv.xkb,
    conv.svg,
    conv.linux_console
    ]

def usage():
    print("Usage: conv.py [-o OUTPUT_DIR] [-g] INPUT_FILE")
    print(" Custom keyboard layout compiler")

MAX_LEVELS = 8

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

symname_defs = {}


def read_symname_defs_file(filename):
    word_split_re = re.compile(r"[ \t()]+")
    with open(filename, "r") as f:
        while True:
            lin = f.readline()
            if not lin: break
            if not lin.startswith("#define"):
                continue
            words = re.split(word_split_re, lin)

            symname = words[1]
            symval = words[2]
            for word in words:
                if word.startswith("U+"):
                    symval = word
                    break

            kname = symname[3:]
            #print([kname, symval])

            if symval.startswith("U+"):
                ksym = int(symval[2:], base=16)
            else:
                ksym = int(symval, base=16)
                if ksym > 0x10000000:
                    ksym -= 0x10000000
                else:
                    continue

            #print([kname, ksym])
            symname_defs[kname] = ksym
    return

read_symname_defs_file("fetch/keysymdef.h")

if debug:
    pprint.pprint(symname_defs)

if not os.path.exists(infile):
    fatal("INPUT_FILE must exist")

indir = os.path.dirname(infile)

layouts = []
partials = []

PAREN_RE = re.compile(r"[()]+")

standard_keydefs = []

def get_part_by_name(s):
    components = re.split(PAREN_RE, s)
    if len(components) < 2:
        if debug:
            print("Missing partial file name: '{}'".format(s))
        filename = components[0]
        partname = None
    else:
        filename, partname, *_ = components
    for x in (partials + layouts + standard_keydefs):
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
        self.already_merged = []
        self.compiled = False
        self.compiled_keys = []
        self.latin = not re.match("^ru($|_)", name)

    def xkbname(self):
        if self.name:
            return "{}({})".format(self.filename, self.name)
        return self.filename

    def __str__(self):
        keys = ""
        for k in self.keys:
            keys += "    {}\n".format(k)
        return """Keydefs<{} ({}) includes={}\n  keys=[\n{}  ] latin={}>""".format(
                repr(self.filename),
                repr(self.name),
                self.includes,
                keys,
                self.latin)

    def __repr__(self):
        return self.__str__()

    def compile(self, indent=""):
        indent1 = indent + " "
        if self.compiled:
            return
        print("{}Compiling '{}'".format(indent, self.xkbname()))
        self.compiled_keys = []
        for inc in self.includes:
            partial = get_part_by_name(inc)

            if not partial:
                print("{}Not merging '{}' into '{}'".format(indent1, inc, self.xkbname()))
            else:
                partial.compile(indent1)
                print("{}Merging '{}' into '{}'; already: {}".format(indent1, inc, self.xkbname(), self.already_merged))
                self.merge_keys(partial.xkbname(), partial.compiled_keys)
        self.merge_keys("<self>", self.keys)
        self.compiled_keys.sort()
        if debug:
            print("Compiled '{}': {}".format(self.xkbname(), self.compiled_keys))
        self.compiled = True

    def merge_keys(self, ident, keys):
        self.already_merged.append(ident)
        for key in keys:
            merged = False
            if key[0] == "key":
                for k1 in self.compiled_keys:
                    if k1[:2] == key[:2]:
                        merged = True
                        for lv, ksym in enumerate(key[2]):
                            if ksym:
                                k1[2][lv] = ksym
            if not merged:
                self.compiled_keys.append(copy.deepcopy(key))

    def get_keysym(self, keycode, level):
        for directive in self.compiled_keys:
            if directive[0] == "key" and directive[1] == keycode:
                return directive[2][level-1]

def keys_to_defs(filename, name, keys, additional_directives):
    kd = Keydefs(filename, name)
    kd_keys = []

    def process_keydef(kcode, syms):
        syms = copy.copy(syms)
        if isinstance(syms, str):
            syms = [syms.lower(), syms]
        for i,sym in enumerate(syms):
            sym = ord(sym)
            syms[i] = "U" + (int_to_base(sym, 16)).zfill(4)
        while len(syms) < MAX_LEVELS:
            syms.append(None)
        keydef = ["key", kcode, copy.deepcopy(syms)]
        if debug:
            print("predefining {} {}: {}".format(filename, name, keydef))
        kd_keys.append(keydef)

    for kn in keys:
        if kn in ["AB","AC","AD","AE"]:
            for col, syms in enumerate(keys[kn], 1):
                col = str(col).zfill(2)
                process_keydef("{}{}".format(kn, col), syms)
        else:
            process_keydef(kn, keys[kn])
    kd.merge_keys(kd.xkbname(), kd_keys)
    kd.merge_keys(kd.xkbname(), additional_directives)
    kd.compiled = True
    if debug:
        print(kd_keys)
        print("Compiled keys {}:\n".format(kd.xkbname(), kd.compiled_keys))
    return kd

standard_keydefs.append(keys_to_defs("us", "", {
    "AE": [ ["1","!"], ["2","@"], ["3","#"], ["4","$"], ["5","%"], ["6","^"], ["7","&"], ["8","*"], ["9","("], ["0",")"], ["-","_"], ["=","+"] ],
    "AD": [ "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", ["[","{"], ["]","}"] ],
    "AC": [ "A", "S", "D", "F", "G", "H", "J", "K", "L", [";",":"], ["'", '"'] ],
    "AB": [ "Z", "X", "C", "V", "B", "N", "M", [",","<"], [".",">"], ["/","?"] ],
    "TLDE": ["`","~"],
    "BKSL": ["\\","|"],
    },
    [
        ["key", "TAB",  ["Tab",   "ISO_Left_Tab", None, None, None, None, None, None]],
        ["key", "SPCE", ["space", "space",        None, None, None, None, None, None]],
    ]))

COMMA_RE = re.compile(r"[ \t]*,[ \t]*")
COLON_COMMA_RE = re.compile(r"[ \t]*[,:][ \t]*")

files_already_read = []

def read_file(filename, as_partials=False, referring_files=[]):
    global debug

    print("Reading {} (as_partials={} refererring_files={})".format(
            filename, as_partials, referring_files))
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

    # prevent a file from including itself
    files_already_read.append(os.path.basename(filename))

    cur_defs = None
    cur_level = 1
    for nl, l in enumerate(lines, 1):
        toks = shlex.split(l)
        if debug:
            print(str(toks))
        if len(toks):
            tok, *args = toks
            if tok == '#':
                True
            elif tok == "symbols":
                expect_argc(1)
                cur_defs = Keydefs(filename_name, args[0])
                if as_partials:
                    print(" In {}: Partial {}".format(filename, args[0]))
                    partials.append(cur_defs)
                else:
                    print(" In {}: Layout {}".format(filename, args[0]))
                    layouts.append(cur_defs)
            elif tok == "include":
                expect_argc(1)
                inc_arg = args[0]
                inc_filename = re.sub("[(].*", "", inc_arg)
                indir_file = os.path.join(indir, inc_filename)
                cur_defs.includes.append(inc_arg)
                if os.path.exists(indir_file) and inc_filename not in files_already_read:
                    read_file(indir_file, True, referring_files + [(filename, nl)])
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
read_file("level3_switch", as_partials=True)
read_file("level5_switch", as_partials=True)

for x in layouts:
    x.compile()

if debug:
    print("\nLayouts =============")
    pprint.pprint(layouts)
    print("\nPartials ============")
    pprint.pprint(partials)

if not os.path.exists(outdir):
    os.mkdir(outdir)

for outm in conv_to_perform:
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
    outm.convert(debug, outmdir, symname_defs, layouts, partials)


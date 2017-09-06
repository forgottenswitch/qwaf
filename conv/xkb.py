import os
import re

name = "xkb"

def filter_include(inc):
    inc = re.sub(r"^(letters|layouts)", "qwaf", inc)
    return inc

def collect_includes(includes):
    ret = []
    for inc in includes:
        inc = filter_include(inc)
        s = '  include "{}"'.format(inc)
        ret.append(s)
    return "\n".join(ret)

def collect_keys(keys):
    ret = []
    for k in keys:
        op, *args = k
        s = ""
        if op == "keytype":
            s += '  key.type = "{}";\n'.format(args[0])
        elif op == "key" or op == "replace_key":
            kcode, levels = args
            replace = ""
            if op == "replace_key":
                replace = "replace "
            s += "  {}key <{}> {{ [ ".format(replace, kcode)
            levels1 = []
            for ksym in levels:
                if not ksym:
                    ksym = "NoSymbol"
                levels1.append(ksym)
            s += ", ".join(levels1)
            s += " ] };"
        elif op == "modifier_key":
            s += "  modifier_map {} {{ <{}> }};".format(args[1], args[0])
        ret.append(s)
    return "\n".join(ret)

class DestinationsForPartials:
    def __init__(self, outdir):
        self.outdir = outdir
        self.fobjs = {}
        self.files = {}

    def __enter__(self):
        return self

    def __exit__(self, except_type, except_val, except_traceback):
        self.close_all()
        if except_type:
            raise except_val

    def add_file(self, src_file, dest_file):
        dest_file = os.path.join(self.outdir, dest_file)
        self.files[src_file] = dest_file
        self.fobjs[src_file] = open(dest_file, "w")

    def close_all(self):
        for src_file in self.fobjs:
            self.fobjs[src_file].close()
        self.fobjs = {}

def convert(debug, outdir, symname_defs, layouts, partials):
    for x in ["symbols", "types", "compat"]:
        try:
            os.mkdir(os.path.join(outdir, x))
        except FileExistsError:
            pass

    # Output layout files (they only include partial files)
    #
    filename_layouts = os.path.join(outdir, "symbols", "qwaf")
    with open(filename_layouts, "w") as f:
        for k in layouts:
            includes = collect_includes(k.includes)
            xkb_symbols = """partial alphanumeric_keys modifier_keys
xkb_symbols "{}" {{
{}
}};

""".format(k.name, includes)
            if debug:
                print("Into {}:".format(filename_layouts))
                print(xkb_symbols, end="")
            f.write(xkb_symbols)

    # Output partial files (the actual key assignments)
    #
    with DestinationsForPartials(outdir) as dest:
        dest.add_file("letters_lat", "symbols/qwaf_lat")
        dest.add_file("letters_cyr", "symbols/qwaf_cyr")
        dest.add_file("hjkl", "symbols/hjkl")
        dest.add_file("level3_switch", "symbols/level3_switch")
        dest.add_file("level5_switch", "symbols/level5_switch")

        for k in partials:
            k_base_filename = os.path.basename(k.filename)
            if debug:
                print("Converting partial: {}".format(k))
            dest_fobj = dest.fobjs[k_base_filename]
            dest_file = dest.files[k_base_filename]

            includes = collect_includes(k.includes)
            includes_nl = "\n"
            if len(includes) == 0:
                includes_nl = ""

            keys = collect_keys(k.keys)
            xkb_symbols = """partial alphanumeric_keys modifier_keys
xkb_symbols "{}" {{
{}{}{}
}};

""".format(k.name, includes, includes_nl, keys)

            if debug:
                print("Into {} (from {}):".format(dest_file, k.filename))
                print(xkb_symbols, end="")
            dest_fobj.write(xkb_symbols)


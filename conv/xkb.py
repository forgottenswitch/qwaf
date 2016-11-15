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

def convert(debug, outdir, keydefs, layouts, partials):
    for x in ["symbols", "types", "compat"]:
        try:
            os.mkdir(os.path.join(outdir, x))
        except FileExistsError:
            pass

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

    filename_cyr = os.path.join(outdir, "symbols", "qwaf_cyr")
    filename_lat = os.path.join(outdir, "symbols", "qwaf_lat")
    filename_hjk = os.path.join(outdir, "symbols", "hjkl")
    filename_lv3 = os.path.join(outdir, "symbols", "level3_hjkl")
    filename_lv5 = os.path.join(outdir, "symbols", "level5_hjkl")

    CYR_RE = re.compile("^letters_cyr")
    LAT_RE = re.compile("^letters_lat")

    with open(filename_cyr, "w") as f_cyr, \
            open(filename_lat, "w") as f_lat, \
            open(filename_hjk, "w") as f_hjk, \
            open(filename_lv3, "w") as f_lv3, \
            open(filename_lv5, "w") as f_lv5:
        for k in partials:
            k_base_filename = os.path.basename(k.filename)

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
            if re.match(LAT_RE, k_base_filename):
                filename_out, f_out = filename_lat, f_lat
            elif re.match(CYR_RE, k_base_filename):
                filename_out, f_out = filename_cyr, f_cyr
            elif k_base_filename == "level3_hjkl":
                filename_out, f_out = filename_lv3, f_lv3
            elif k_base_filename == "level5_hjkl":
                filename_out, f_out = filename_lv5, f_lv5
            else:
                filename_out, f_out = filename_hjk, f_hjk
            if debug:
                print("Into {} (from {}):".format(filename_out, k_base_filename))
                print(xkb_symbols, end="")
            f_out.write(xkb_symbols)


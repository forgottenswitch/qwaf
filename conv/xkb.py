import os
import re

name = "xkb"

def filter_include(inc):
    inc = re.sub(r"^(letters|layouts)", "qwaf", inc)
    return inc

def convert(debug, outdir, keydefs, layouts, partials):
    for x in ["symbols", "types", "compat"]:
        os.mkdir(os.path.join(outdir, x))
    filename = os.path.join(outdir, "symbols", "qwaf")
    with open(filename, "w") as f:
        for k in layouts:
            includes = ""
            for inc in k.includes:
                inc = filter_include(inc)
                includes += "  include '{}'\n".format(inc)
            with open(filename, "a") as f:
                xkb_symbols = """partial alphanumeric
xkb_symbols '{}' {{
{}}};

""".format(k.name, includes)
                if debug:
                    print("Into {}:".format(filename))
                    print(xkb_symbols, end="")
                f.write(xkb_symbols)


import os

name = "xkb"

def convert(debug, outdir, keydefs, layouts, partials):
    for x in ["symbols", "types", "compat"]:
        os.mkdir(os.path.join(outdir, x))
    for k in layouts:
        includes = ""
        for inc in k.includes:
            includes += "  include '{}'\n".format(inc)
        filename = os.path.join(outdir, "symbols", k.filename)
        with open(filename, "a") as f:
            xkb_symbols = """partial alphanumeric
xkb_symbols '{}' {{
{}}};

""".format(k.name, includes)
            if debug:
                print("Into {}:".format(filename))
                print(xkb_symbols, end="")
            f.write(xkb_symbols)

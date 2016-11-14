import os
import re

name = "svg"

def convert(debug, outdir, keydefs, layouts, partials):
    outldir = os.path.join(outdir, "layouts")
    outpdir = os.path.join(outdir, "partials")

    for odir in [outldir, outpdir]:
        try:
            os.mkdir(outldir)
        except FileExistsError:
            pass

    key_w = 100
    key_h = key_w
    key_b = 20

    for lt in layouts:
        keys = []
        for k in lt.compiled_keys:
            directive, *args = k
            if directive == "key":
                keycode, keysyms = args
                if keycode[:2] in ["AB", "AC", "AD", "AE"] or keycode in ["TLDE", "BKSL"]:
                    if keycode == "TLDE":
                        column = 0
                    elif keycode == "BKSL":
                        column = 13
                    else:
                        column = int(keycode[2:])
                    if keycode.startswith("AB"):
                        xpos = int(key_w * 2.4 + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int((key_b + key_w) * 3 + key_b)
                    elif keycode.startswith("AC"):
                        xpos = int(key_w * 1.8 + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int((key_b + key_w) * 2 + key_b)
                    elif keycode.startswith("AD"):
                        xpos = int(key_w * 1.5 + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int((key_b + key_w) * 1 + key_b)
                    else:
                        xpos = int(key_w * 1.0 + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int(key_b)
                    keys.append("""<rect x="{}" y="{}" width="{}" height="{}" fill="blue" />""".format(xpos, ypos, key_w, key_h))

        svg_name = os.path.join(outldir, lt.name + ".svg")
        if debug:
            print("'{}({})' into '{}'".format(lt.filename, lt.name, svg_name))

        with open(svg_name, "w") as f:
            f.write("""
<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
    <rect x="0" y="0" width="{kbd_w}" height="{kbd_h}" fill="white" />
    {keys}
""".format(
        kbd_w=(key_w*15+key_b*16),
        kbd_h=(key_h*5+key_b*6),
        keys="\n".join(keys),
        ))
            f.write("</svg>")


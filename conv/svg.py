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

    tilde_mul = 1.0
    tab_mul = 1.5
    caps_mul = 1.8
    lshift_mul = 2.4

    for lt in layouts:
        keys = []

        # r/l side dividing line
        muls = [tilde_mul, tab_mul, caps_mul, lshift_mul]
        for row, mul in enumerate(muls):
            xpos1 = key_b + key_w * mul + (key_b + key_w) * 5 + key_b * 0.5
            try:
                xpos2 = xpos1 + key_w * (muls[row+1] - mul)
            except:
                xpos2 = None
            ypos1 = (key_b + key_h) * row + key_b*0.5
            ypos2 = ypos1 + key_h + key_b
            keys.append("""<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />""".format(xpos1, ypos1, xpos1, ypos2, key_b*0.1 ))
            if xpos2:
                keys.append("""<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />""".format(xpos1, ypos2, xpos2, ypos2, key_b*0.1 ))

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
                        xpos = int(key_w * lshift_mul + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int((key_b + key_w) * 3 + key_b)
                    elif keycode.startswith("AC"):
                        xpos = int(key_w * caps_mul + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int((key_b + key_w) * 2 + key_b)
                    elif keycode.startswith("AD"):
                        xpos = int(key_w * tab_mul + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int((key_b + key_w) * 1 + key_b)
                    else:
                        xpos = int(key_w * tilde_mul + (key_b + key_w) * (column-1) + key_b * 2)
                        ypos = int(key_b)

                    ksym = str(keysyms[0]).capitalize()
                    keys.append("""<rect x="{}" y="{}" width="{}" height="{}" fill="#E9B96E" />""".format(xpos, ypos, key_w, key_h))
                    keys.append("""<text x="{}" y="{}" fill="white" stroke="black" stroke-width="{}"
        font-family="sans-serif" font-size="{}px">{}</text>""".format(xpos+key_w*0.35, ypos+key_h*0.6, key_w*0.02, key_w*0.4, ksym))

        svg_name = os.path.join(outldir, lt.name + ".svg")
        if debug:
            print("'{}({})' into '{}'".format(lt.filename, lt.name, svg_name))

        with open(svg_name, "w") as f:
            f.write("""
<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
    <rect x="0" y="0" width="{kbd_w}" height="{kbd_h}" fill="gray" />
    {keys}
""".format(
        kbd_w=(key_w*15+key_b*16),
        kbd_h=(key_h*5+key_b*6),
        keys="\n".join(keys),
        ))
            f.write("</svg>")

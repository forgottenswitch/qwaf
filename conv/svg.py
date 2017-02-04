import os
import re
import sys

name = "svg"

special_ksyms = {
    "ISO_Level5_Shift": "Lv5",
    "ISO_Level3_Latch": "Lv3",
}

key_w = 100
key_h = key_w
key_b = 20

tilde_mul = 1.0
tab_mul = 1.5
caps_mul = 1.8
lshift_mul = 2.4

def convert(debug, outdir, symname_defs, layouts, partials):
    outldir = os.path.join(outdir, "layouts")
    outpdir = os.path.join(outdir, "partials")

    for odir in [outldir, outpdir]:
        try:
            os.mkdir(outldir)
        except FileExistsError:
            pass

    for lt in layouts:
        svg_ops = []
        hands_dividing_line(svg_ops)

        for k in lt.compiled_keys:
            directive, *args = k

            if directive == "key":
                keycode, keysyms = args
                if debug:
                    print(["svg: lkey", lt.name, keycode, keysyms])

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

                    svg_ops.append("""<rect x="{}" y="{}" width="{}" height="{}" rx="{}" ry="{}" fill="white" stroke="black" stroke-width="{}"/>""".format(
                        xpos, ypos, key_w, key_h, key_w*0.1, key_h*0.1, key_w*0.01))

                    ksym1 = str(keysyms[0])
                    ksym2 = str(keysyms[1])

                    def to_utf_char(s):
                        code = None
                        if s is None:
                            return
                        if s in special_ksyms:
                            return special_ksyms[s]
                        if s not in symname_defs:
                            if s.startswith("U"):
                                code = int(s[1:], base=16)
                        else:
                            code = symname_defs.get(s)
                        if code:
                            return "&#{};".format(code)
                        return s

                    ksym1 = to_utf_char(ksym1)
                    ksym2 = to_utf_char(ksym2)

                    def same_letter(s1, s2):
                        if s1.startswith("&#"): s1 = chr(int(s1[2:-1]))
                        if s2.startswith("&#"): s2 = chr(int(s2[2:-1]))
                        if s1.capitalize() == s2:
                            return True

                    if not same_letter(ksym1, ksym2):
                        svg_ops.append("""<text x="{}" y="{}" fill="black" font-size="{}px">{}</text>""".
                                format(xpos+key_w*0.3, ypos+key_h*0.85, key_w*0.4, ksym1))
                        svg_ops.append("""<text x="{}" y="{}" fill="black" font-size="{}px">{}</text>""".
                                format(xpos+key_w*0.3, ypos+key_h*0.35, key_w*0.4, ksym2))
                    else:
                        svg_ops.append("""<text x="{}" y="{}" text-anchor="middle" fill="black" font-size="{}px">{}</text>""".
                                format(xpos+key_w*0.5, ypos+key_h*0.6, key_w*0.4, ksym2))

        svg_name = os.path.join(outldir, lt.name + ".svg")
        if debug:
            print("'{}({})' into '{}'".format(lt.filename, lt.name, svg_name))

        with open(svg_name, "w") as f:
            f.write("""
<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
    <rect x="0" y="0" width="{kbd_w}" height="{kbd_h}" fill="white" />
{svg_ops}
</svg>""".format(
        kbd_w=(key_w*15+key_b*16),
        kbd_h=(key_h*5+key_b*6),
        svg_ops="\n".join(svg_ops),
        ))

SPACE_RE = re.compile(r"[ \t]+")

def hands_dividing_line(svg_ops):
    muls = [tilde_mul, tab_mul, caps_mul, lshift_mul]
    for row, mul in enumerate(muls):
        xpos1 = key_b + key_w * mul + (key_b + key_w) * 5 + key_b * 0.5
        try:
            xpos2 = xpos1 + key_w * (muls[row+1] - mul)
        except:
            xpos2 = None
        ypos1 = (key_b + key_h) * row + key_b*0.5
        ypos2 = ypos1 + key_h + key_b
        svg_ops.append('<line x1="{}" y1="{}" x2="{}" y2="{}"'
                       ' stroke="black" stroke-width="{}"'
                       ' />'.format(xpos1, ypos1, xpos1, ypos2, key_b*0.1))
        if xpos2:
            svg_ops.append('<line x1="{}" y1="{}" x2="{}" y2="{}"'
                           ' stroke="black" stroke-width="{}"'
                           ' />'.format(xpos1, ypos2, xpos2, ypos2, key_b*0.1))


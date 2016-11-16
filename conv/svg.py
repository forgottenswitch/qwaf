import os
import re
import sys

name = "svg"

ksyms = {}

special_ksyms = {
    "ISO_Level5_Shift": "Lv5",
    "ISO_Level3_Latch": "Lv3",
}

def convert(debug, outdir, keydefs, layouts, partials):
    read_keysymdefs(outdir)

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

                    keys.append("""<rect x="{}" y="{}" width="{}" height="{}" fill="#E9B96E" />""".format(xpos, ypos, key_w, key_h))

                    ksym1 = str(keysyms[0])
                    ksym2 = str(keysyms[1])

                    def to_utf_char(s):
                        if s is None:
                            return
                        if s in special_ksyms:
                            return special_ksyms[s]
                        if s not in ksyms:
                            if s.startswith("U"):
                                return int(s[1:], base=16)
                            return s
                        code = ksyms.get(s)
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
                        keys.append("""<text x="{}" y="{}" fill="white" stroke="black" stroke-width="{}" font-size="{}px">{}</text>""".
                                format(xpos+key_w*0.3, ypos+key_h*0.85, key_w*0.01, key_w*0.4, ksym1))
                        keys.append("""<text x="{}" y="{}" fill="white" stroke="black" stroke-width="{}" font-size="{}px">{}</text>""".
                                format(xpos+key_w*0.3, ypos+key_h*0.35, key_w*0.01, key_w*0.4, ksym2))
                    else:
                        keys.append("""<text x="{}" y="{}" text-anchor="middle" fill="white" stroke="black" stroke-width="{}" font-family="sans-serif" font-size="{}px">{}</text>""".
                                format(xpos+key_w*0.5, ypos+key_h*0.6, key_w*0.018, key_w*0.4, ksym2))

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

SPACE_RE = re.compile(r"[ \t]+")

def read_keysymdefs(outdir):
    gendir = os.path.dirname(outdir)
    progdir = os.path.dirname(gendir)

    fetchdir = os.path.join(progdir, "fetch")
    keysym_h = os.path.join(fetchdir, "keysymdef.h")

    with open(keysym_h, "r") as f:
        while True:
            lin = f.readline()
            if not lin:
                break
            if not lin.startswith("#define"):
                continue
            words = re.split(SPACE_RE, lin)

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
            ksyms[kname] = ksym


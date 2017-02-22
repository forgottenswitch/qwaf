import os
import re
import sys

name = "svg"

special_ksyms = {
    "ISO_Level5_Lock": "⇪5",
    "ISO_Level5_Shift": "⇧5",
    "ISO_Level3_Latch": "⇧⇧3",
    "ISO_Level2_Latch": "⇧⇧",
    "ISO_Next_Group": "↓⌨",
    "ISO_Prev_Group": "↑⌨",
    "Tab": "↹", "ISO_Left_Tab": "↹",
    "Left": "←", "Up": "↑",
    "Down": "↓", "Right": "→",
    "XF86Undo": "↶", "XF86Redo": "↷",
    "XF86Back": "⇽", "XF86Forward": "⇾",
    "Home": "⇇",
    "Page_Up": "⇈",
    "End": "⇉",
    "Page_Down": "⇊",
    "Return": "↵",
    "Escape": "Esc",
    "BackSpace": "⌫",
    "Delete": "⌦",
    "Menu": "▤",
    "Multi_key": "+⌨",
    "None": "",
}

key_w = 100
key_h = key_w
key_b = 20

tilde_mul = 1.0
tab_mul = 1.5
caps_mul = 1.8
lshift_mul = 2.4

CausesAnotherLevel = None

def convert(debug, outdir, symname_defs, layouts, partials):
    outldir = os.path.join(outdir, "layouts")
    outpdir = os.path.join(outdir, "partials")

    for odir in [outldir, outpdir]:
        try:
            os.mkdir(outldir)
        except FileExistsError:
            pass

    for lt in layouts:
        global CausesAnotherLevel
        CausesAnotherLevel = {}
        for base_lv in [1, 3, 5]:
            svg_ops = []
            hands_dividing_line(svg_ops)

            for k in lt.compiled_keys:
                directive, *args = k
                if directive == "key":
                    kcode, ksyms = args
                    ksym1 = str(ksyms[base_lv-1])
                    ksym2 = str(ksyms[base_lv])
                    output_key(svg_ops, kcode, ksym1, ksym2, symname_defs, lt, debug, base_lv)

            svg_filename = lt.name
            if base_lv != 1:
                svg_filename += "-lv{}".format(base_lv)
            svg_name = os.path.join(outldir, svg_filename + ".svg")
            if debug:
                print("'{}({})' into '{}'".format(lt.filename, lt.name, svg_name))

            with open(svg_name, "w") as f:
                rows, cols = 4, 14
                f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
                        '    <rect x="0" y="0" width="{kbd_w}" height="{kbd_h}" fill="white" />\n'
                        '{svg_ops}\n'
                        '</svg>'.format(
                            kbd_w=(key_w*cols+key_b*(cols+1)),
                            kbd_h=(key_h*rows+key_b*(rows+1)),
                            svg_ops="\n".join(svg_ops)
                            ))

U_hexdigit = re.compile("U[0-9a-fA-F]+$")

def note_if_causes_another_level(keycode, keysym):
    global CausesAnotherLevel
    if keysym in ["ISO_Level3_Shift", "ISO_Level3_Latch"]:
        CausesAnotherLevel[str(keycode)] = 3
    if keysym in ["ISO_Level5_Shift", "ISO_Level5_Latch"]:
        CausesAnotherLevel[str(keycode)] = 5

def causes_this_level(keycode, level):
    if str(keycode) in CausesAnotherLevel:
        if CausesAnotherLevel[str(keycode)] == level:
            return True

def output_key(svg_ops, keycode, keysym1, keysym2, symname_defs, lt, debug, base_lv):
    if debug:
        print(["svg: lkey", lt.name, keycode, keysym1, keysym2])

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

        note_if_causes_another_level(keycode, keysym1)
        if causes_this_level(keycode, base_lv):
            fill_color = "grey"
        else:
            fill_color = "white"

        svg_ops.append('<rect x="{}" y="{}" width="{}" height="{}"'
                       ' rx="{}" ry="{}" fill="{}" stroke="black" stroke-width="{}"'
                       ' />'.format(xpos, ypos, key_w, key_h, key_w*0.1, key_h*0.1,
                                    fill_color, key_w*0.01))

        def to_utf_char(s):
            code = None
            if s is None:
                return
            if s in special_ksyms:
                return special_ksyms[s]
            if s not in symname_defs:
                if re.match(U_hexdigit, s):
                    code = int(s[1:], base=16)
            else:
                code = symname_defs.get(s)
            if code:
                return "&#{};".format(code)
            return s

        ksym1 = to_utf_char(keysym1)
        ksym2 = to_utf_char(keysym2)

        def same_letter(s1, s2):
            if s1.startswith("&#"): s1 = chr(int(s1[2:-1]))
            if s2.startswith("&#"): s2 = chr(int(s2[2:-1]))
            if s1.capitalize() == s2:
                return True

        class label:
            def __init__(self, ksym, ypos_offset):
                self.font_size = key_w * 0.4
                self.font_style = "bold"
                self.ksym = ksym
                self.xpos = xpos + key_w*0.3
                self.ypos = ypos + key_h*(0.35 + ypos_offset)
                if self.ksym.startswith("dead_"):
                    self.ksym = self.ksym[5:]
                    self.font_size *= 0.7
                    self.font_style = "italic"
                    self.xpos = xpos + key_w*0.05
                return

        if not same_letter(ksym1, ksym2):
            lb1 = label(ksym1, 0.5)
            lb2 = label(ksym2, 0)
            svg_ops.append('<text x="{}" y="{}" fill="black"'
                           ' font-size="{}px" font-style="{}"'
                           ' >{}</text>'.format(
                               lb1.xpos, lb1.ypos,
                               lb1.font_size, lb1.font_style,
                               lb1.ksym))
            svg_ops.append('<text x="{}" y="{}" fill="black"'
                           ' font-size="{}px" font-style="{}"'
                           ' >{}</text>'.format(
                               lb2.xpos, lb2.ypos,
                               lb2.font_size, lb2.font_style,
                               lb2.ksym))
        else:
            svg_ops.append('<text x="{}" y="{}" fill="black"'
                           ' font-size="{}px" font-style="{}"'
                           ' text-anchor="middle"'
                           ' >{}</text>'.format(
                               xpos+key_w*0.5, ypos+key_h*0.6,
                               key_w * 0.5, "bold",
                               ksym2))

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


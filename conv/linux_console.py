import os
import re
from conv.utils import int_to_base

name = "linux_console"

ModifierSyms = [
        "ISO_Level5_Shift", "ISO_Level5_Latch",
        "ISO_Level3_Shift", "ISO_Level3_Latch",
        ]

Control_capable_keys = [
        "underscore", "backslash",
        "bracketleft", "bracketright", # Control_bracketleft => Escape
]

Meta_capable_keys = [
        "grave",
        "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine", "zero",
        "exclam", "at", "numbersign", "dollar", "percent",
        "asciicircum", "minus", "equal", "backslash", "bar",
        "comma", "greater", "less", "slash", "question",
        "semicolon", "apostrophe",
        "Tab", "Delete", "space",
]

Translations = {
        "NoSymbol": "nul",
        "VoidSymbol": "nul",

        "Backspace": "BackSpace",
        "Delete": "Remove",
        "Next": "PageDown",
        "Prior": "PageUp",

        "Multi_key": "Compose",
        "Menu": "nul",
        "ISO_Left_Tab": "Meta_Tab",
        "Print": "nul",
        "XF86Back": "nul",
        "XF86Forward": "nul",
        "Undo": "nul",
        "Redo": "nul",

        "ShiftL": "Uncaps_Shift",
        "ShiftR": "Uncaps_Shift",
        "ISO_Level2_Shift": "Uncaps_Shift",
        "ISO_Level2_Latch": "Uncaps_Shift",

        "ISO_Level3_Shift": "AltGr",
        "ISO_Level3_Latch": "AltGr",
        "ISO_Level3_Lock": "AltGr_Lock",

        "ISO_Level5_Shift": "ShiftL",
        "ISO_Level5_Latch": "ShiftL",
        "ISO_Level5_Lock": "ShiftL_Lock",

        "dead_invertedbreve": "nul",
        "dead_greek": "nul",
        "dead_hook": "nul",
        "dead_abovedot": "nul",
        "dead_belowdot": "nul",
        "dead_doublegrave": "nul",
        "dead_belowtilde": "nul",
        "dead_belowcomma": "nul",
        "dead_abovecomma": "nul",
        "dead_abovering": "nul",
        "dead_belowring": "nul",
        "dead_abovereversedcomma": "nul",
        "dead_belowcircumflex": "nul",
        "dead_currency": "nul",
        "dead_belowdiaeresis": "nul",
        "dead_stroke": "nul",
        "dead_horn": "nul",
        "dead_macron": "nul",
        "dead_belowmacron": "nul",
        "dead_belowbreve": "nul",
}

Digits = {
        "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
        "6": "six", "7": "seven", "8": "eight", "9": "nine", "0": "zero",
        }

Unicode_re = re.compile(r"U[0-9a-fA-F]{1,4}$")

Redirs = {
        # This should be kept in sync with "redirs" from ./hjkl
        "ISO_Fast_Cursor_Left": "Left",
        "ISO_Fast_Cursor_Down": "Down",
        "ISO_Fast_Cursor_Up": "Up",
        "ISO_Fast_Cursor_Right": "Right",
        #
        "ISO_Partial_Line_Down": "Next",
        "ISO_Partial_Line_Up": "Prior",
        "ISO_Partial_Space_Left": "Home",
        "ISO_Partial_Space_Right": "End",
        #
        "ISO_Set_Margin_Left": "BackSpace",
        "ISO_Set_Margin_Right": "Delete",
        #
        "ISO_Release_Margin_Left": "Return",
        "ISO_Release_Margin_Right": "Insert",
        "ISO_Release_Both_Margins": "Escape",
}

UnknownSymnames = [
        "horizconnector", "schwa", "SCHWA",
        "leftdoublequotemark", "rightdoublequotemark",
        "leftsinglequotemark", "rightsinglequotemark",
        "doublelowquotemark", "singlelowquotemark",
        "decimalpoint", "underbar", "rightcaret",
        ]

GroupModifier = "shiftr"
GroupTranslations = {
        "ISO_Next_Group": "ShiftR_Lock",
        "ISO_Prev_Group": "ShiftR_Lock",
}

Keycodes = {
        "AE01": 2, "AD01": 16, "AC01": 30, "AB01": 44,
        "BKSL": 43, "TAB": 15, "TLDE": 41, "SPCE": 57,
}

Levels = [
        "",             # 1
        "shift",        # 2
        "altgr",        # 3
        "altgr shift",  # 4
        "shiftl",       # 5
        "shiftl shift", # 6
        ]

SymnameDefs = {}

def convert(debug, outdir, symname_defs, layouts, partials):
    global SymnameDefs
    SymnameDefs = symname_defs
    for kl in layouts:
        if kl.name == "qwaf":
            kl_us = kl
    for kl in layouts:
        if kl.latin:
            kname = kl.name
            if kname == "qwaf": kname = "us"
            out_name = "qwaf_{}.map".format(kname)
            dual_layout(kl, None, outdir, out_name)
        else:
            out_name = "qwaf_us-{}.map".format(kl.name)
            dual_layout(kl_us, kl, outdir, out_name)
        if debug:
            print("{} -> {}".format(kl.name, out_name))

Modifiers = ["control", "alt", "control alt"]

KeysymMods = { "control": "Control", "alt": "Meta", "control alt": "Meta_Control", }

modifier_space1 = max([ len(x) for x in Modifiers ]) + 1
linux_level_space = max([ len(x) for x in Levels ]) + 1

Modifiers = [None] + Modifiers

SPACES = [ " " * x for x in range(0,32) ]

def spacepad(s, l):
    l_to_add = l - len(s)
    if l_to_add > 0:
        s += SPACES[l_to_add]
    return s

def is_latin_letter(s):
    if not s: return False
    if len(s) != 1: return False
    return (s >= 'a' and s <= 'z') or (s >= 'A' and s <= 'Z')

DefaultKeycodes = None

def add_undefined_keycodes_to_second_group(dest_fobj, outdir, keycodes_defined):
    global DefaultKeycodes
    if not DefaultKeycodes:
        DefaultKeycodes = {}
        spaces_re = r"[ \t]+"
        default_map_filename = os.path.join(outdir, "../../fetch/linux_default.map")
        kcode, lines = None, []
        nul_re = "[ \t]nul[ \t]*$"
        with open(default_map_filename, "rb") as f:
            def push_kcode():
                nonlocal kcode, lines
                nonempty = False
                for l in lines:
                    if not re.search(nul_re, l):
                        nonempty = True
                if nonempty and kcode \
                        and len(lines) and not lines[0].endswith("Caps_Lock\n"):
                    DefaultKeycodes[str(kcode)] = lines
            for l in f.readlines():
                try: l = l.decode("UTF-8")
                except Exception as e: continue
                if l.startswith("keycode"):
                    if kcode: push_kcode()
                    words = re.split(spaces_re, l)
                    kcode = words[1]
                    ksym1, ksym2 = words[3], words[4]
                    lines = [ "keycode {} = {}\n".format(kcode, ksym1),
                              "\tshift keycode {} = {}\n".format(kcode, ksym2) ]
                elif l.startswith("string") or l.startswith("compose"):
                    break
                else:
                    lines.append(l)
            if kcode: push_kcode()
    for kcode_str in DefaultKeycodes:
        kcode = int(kcode_str)
        if kcode not in keycodes_defined:
            lines = DefaultKeycodes[kcode_str]
            dest_fobj.write("\n");
            for l in lines:
                dest_fobj.write(GroupModifier)
                dest_fobj.write(" ")
                dest_fobj.write(l)
    caps_to_ctrl_map_filename = os.path.join(outdir, "../../fetch/linux_caps_to_ctrl.map")
    with open(caps_to_ctrl_map_filename, "r") as f:
        lines = []
        for l in f.readlines():
            l = l.rstrip()
            if len(l):
                lines.append(l)
        dest_fobj.write("\n")
        for l in lines:
            dest_fobj.write(l + "\n")
        dest_fobj.write("\n")
        for l in lines:
            dest_fobj.write(GroupModifier + " " + l + "\n")

def dual_layout(kl1, kl2, outdir, out_filename):
    out_filename = os.path.join(outdir, out_filename)
    keycodes_defined = []
    with open(out_filename, "w") as dest_fobj:
        dest_fobj.write('include "linux-keys-bare.inc"\n\n')
        one_layout(kl1, None, dest_fobj, kl2, keycodes_defined)
        if kl2:
            dest_fobj.write('\n')
            one_layout(kl2, kl1, dest_fobj, kl2, keycodes_defined)
        add_undefined_keycodes_to_second_group(dest_fobj, outdir, keycodes_defined)
    return

def one_layout(kl, kl_qwerty, dest_fobj, dual, keycodes_defined):
    for k in kl.compiled_keys:
        directive, *args = k
        if directive == "key":
            keycode, keysyms = args
            keysyms = keysyms[:6]
            key_def_lines = []

            for modifier in Modifiers:
                mod_capit = (modifier or "key").capitalize()

                if not modifier: key_def_lines.append("#")
                key_def_lines.append("# {} <{}>".format(mod_capit, keycode));
                if not modifier:
                    keysyms1 = [ Redirs.get(x) or x for x in keysyms ]
                    key_def_lines.append("# " + str(keysyms1))
                if not modifier: key_def_lines.append("#")

                linux_kcode = 0
                if keycode in Keycodes:
                    linux_kcode = Keycodes[keycode]
                else:
                    prefix = keycode[:2]
                    n = int(keycode[2:])
                    if prefix in ["AE", "AD", "AC", "AB"]:
                        linux_kcode = Keycodes[prefix+"01"] + n-1
                    else:
                        raise Exception("Unable to translate keycode '{}'".format(keycode))
                keycodes_defined.append(linux_kcode)

                for lv, ksym in enumerate(keysyms, 1):
                    if not ksym: ksym = "NoSymbol"

                    modifier_str = "plain"
                    modifier_space = modifier_space1
                    if not modifier and lv > 1: modifier_str = ""
                    if modifier: modifier_str = modifier
                    if kl_qwerty:
                        if modifier_str == "plain": modifier_str = ""
                        modifier_str = GroupModifier + " " + modifier_str
                        modifier_space += len(GroupModifier) + 1
                    if modifier_str:
                        modifier_str = spacepad(modifier_str, modifier_space)
                    else:
                        modifier_str = SPACES[modifier_space]

                    if ksym in Digits:
                        ksym = Digits[ksym]
                    elif dual and ksym in GroupTranslations:
                        ksym = GroupTranslations[ksym]
                    elif ksym in Redirs:
                        ksym = Redirs[ksym]
                    elif ksym and re.match(Unicode_re, ksym):
                        ksym_code_hex = ksym[1:]
                        ksym_code = int(ksym_code_hex, base=16)
                        if ksym_code < 128:
                            for symname in SymnameDefs:
                                if SymnameDefs[symname] == ksym_code:
                                    if symname in UnknownSymnames:
                                        ksym = "U+" + ksym_code_hex
                                    else:
                                        ksym = symname
                        else:
                            ksym = "U+" + ksym_code_hex
                    elif ksym and (ksym.startswith("Cyrillic_") or ksym in UnknownSymnames):
                        try:
                            ksym_utf = SymnameDefs[ksym]
                        except KeyError as e:
                            print("SymnameDefs:")
                            print(SymnameDefs)
                            raise e
                        ksym = "U+" + int_to_base(ksym_utf, 16).zfill(4)

                    # not elif because of Redirs
                    if ksym in ["Next", "Prior"] and (lv % 2) == 0:
                        if ksym == "Next":  ksym = "Decr_Console"
                        if ksym == "Prior": ksym = "Incr_Console"

                    if modifier:
                        if ksym in ModifierSyms:
                            ksym = ksym
                        else:
                            if kl_qwerty:
                                ksym_qwerty = kl_qwerty.get_keysym(keycode, lv)
                                if (ksym not in ModifierSyms) and is_latin_letter(ksym_qwerty):
                                    ksym = ksym_qwerty
                            if is_latin_letter(ksym):
                                if modifier.startswith("control"): ksym = ksym.lower()
                                ksym = "{}_{}".format(KeysymMods[modifier], ksym)
                            elif (modifier == "control") and (ksym in Control_capable_keys):
                                if ksym == "bracketleft": ksym = "Escape"
                                else: ksym = "Control_{}".format(ksym)
                            elif (modifier == "alt") and (ksym in Meta_capable_keys):
                                ksym = "Meta_{}".format(ksym)
                            else:
                                ksym = "NoSymbol"

                    # Duplicate Level3_Latch on the altgr level
                    # (so that it does not lock)
                    if lv in [3, 4] and keysyms[0] == "ISO_Level3_Latch":
                        ksym = "ISO_Level3_Latch"

                    if lv > len(Levels): continue
                    linux_level = Levels[lv-1]
                    if lv == 1: linux_level = ""
                    if linux_level:
                        linux_level = spacepad(linux_level, linux_level_space)
                    else:
                        linux_level = SPACES[linux_level_space]

                    linux_ksym = ksym
                    if ksym in Translations:
                        linux_ksym = Translations[ksym]

                    key_def_lines.append("{}{}keycode {} = {}".format(
                        modifier_str, linux_level,
                        linux_kcode, linux_ksym))

            key_def = "\n".join(key_def_lines)
            dest_fobj.write(key_def)
            dest_fobj.write("\n\n")
    return


QWAF
====

Latin/Cyrillic keyboard layout trying to be similar to Qwerty.

The `hjkl` "module" makes `,` a prefix, `;` a modifier,
`,m` a layout switcher, and `,n` a Compose key.

Currently XKB-only.

International/Dvorak/etc. variants almost aren't tested.

Running on XKB
--------------
To try:
```sh
make
./examples/run_xkb_example.sh
./examples/run_example.sh 1
```
(Ignore the error and lots of warnings it would give).

Or assemble an `.xkb` file (like `examples/qwaf_hjkl.xkb`), and run:
```sh
xkbcomp -I"/path/to/qwaf"/gen/xkb /path/to/xkb/file $DISPLAY
```

To install [for current user], put the above in a file, like `~/xkb.sh`
and add the `sh ~/xkb.sh` to autostart
(by putting this into `~/.xinitrc`, or tweaking desktop settings).

Notes on XKB
------------
Shift-selection with keys accessible through `;` does not work in MonoDevelop and Java apps.
The workaround is active by default, but has problems under Xserver 1.18.1 - 1.18.4.
To disable it in custom `.xkb` file, add `hjkl(lv5)` to `xkb_symbols`.

As the `xkbcomp` cannot distinguish between system and non-system includes,
all generated xkb files under have nonstandard names.

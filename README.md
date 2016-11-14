QWAF
====

Latin/cyrillic keyboard layout trying to be similar to Qwerty.

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
xkbcomp -I"/path/to/qwaf/gen/xkb" /path/to/xkb/file $DISPLAY
```

To install QWAF [for current user], put the above in a file, like `~/xkb.sh`
and add the `sh ~/xkb.sh` to autostart
(by putting this into `~/.xinitrc`, or tweaking desktop settings).

Caveats with XKB
----------------
Shift-selection with keys accessible through `;` does not work in MonoDevelop and Java apps.
The workaround is active by default, but has problems under Xserver 1.18.1 - 1.18.4.
If you are assembling your own `.xkb` file, check the output of `X -version`.
To disable the workaround, add `hjkl(lv5)` to `xkb_symbols`.

As the `xkbcomp` cannot distinguish between system and non-system includes,
all files under `xkb/` have "odd"/unique names.

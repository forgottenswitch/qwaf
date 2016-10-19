QWAF
====

Qwerty-like keyboard layout.
Currently for Xorg (XKB) only.
Comes with a (phonetic) cyrillic variant.

Has an `hjkl` "module", which makes `,` a prefix, `;` a modifier,
`,m` a layout switcher, and `,n` a Compose key.

Is intended to be ergonomic and intuitive for a QWERTY user.
Dvorak and international variants need testing, through.

Running
-------
To try:
```sh
cd qwaf/examples
./run_example.sh
./run_example.sh 1
```
(Even when successfull, it will still give an error and lots of warnings).

Or assemble your own `.xkb` file (like `examples/qwaf_hjkl.xkb`),
and run (without a space after `-I`):
```sh
xkbcomp -I"path/to/qwaf/" path/to/xkb/file $DISPLAY
```
To launch it at login, put the above in, say, `~/xkb.sh` file,
and add the `sh ~/xkb.sh` to autostart
(by putting it into `~/.xinitrc`, or tweaking desktop settings).

Implementation notes
--------------------
As the `xkbcomp` cannot distinguish between system and non-system includes,
all files under `xkb/` have "odd"/unique names.

Bugs
----
Shift-selection with keys accessible through `;` does not work in MonoDevelop and Java apps.
The workaround is active by default, but has problems under Xserver 1.18.1 - 1.18.4.
If you are assembling your own `.xkb` file, check the output of `X -version`.
To disable the workaround, add the `hjkl(lv5)` to `xkb_symbols`.

License
-------
MIT license.

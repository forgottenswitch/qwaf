QWAF
====

Qwerty-like keyboard layout.
Currently for Xorg (XKB) only.
Comes with a (phonetic) cyrillic variant.

Has an `hjkl` "module", which makes `,` a prefix, `;` a modifier,
`,m` a layout switcher, and `,n` a Compose key.

Running
-------
To try:
```sh
cd qwaf/examples
./run_example.sh
./run_example.sh 1
```
(It will give (lots of) error/warnings even when successfull).

Or assemble your own `.xkb` file (like the `examples/qwaf_hjkl.xkb`),
and run (note no space after `-I`):
```sh
xkbcomp -I"path/to/qwaf/" path/to/xkb/file $DISPLAY
```
To launch it at login, put the above in, say, `~/xkb.sh` file,
and add the `sh ~/xkb.sh` to autostart
(by putting it into `~/.xinitrc`, or tweaking desktop settings).

Implementation notes
--------------------
As the `xkbcomp` cannot distinguish between system and non-system includes,
all files under `xkb/` need to have "odd"/unique names.

Usability notes
---------------
Qwaf is intended to be ergonomic and intuitive for a QWERTYist.
Dvorak and international variants need testing, through.

License
-------
MIT license.

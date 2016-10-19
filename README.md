QWAF
====

Qwerty-like keyboard layout.
Currently for Xorg (XKB) only.
Comes with a (phonetic) cyrillic variant.

Has an `hjkl` variant, which makes `,` a prefix, and `;` a modifier.

Running
-------
To try:
```sh
cd qwaf/examples
./run_example.sh
./run_example.sh 1
```
(It will give (lots of) error/warnings even when successfull).

Or assemble your own `.xkb` file
(like one in `examples/`), and run (note no space after `-I`):
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

License
-------
MIT license.

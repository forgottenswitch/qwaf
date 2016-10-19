QWAF
====

Qwerty-like keyboard layout for Xserver (XKB).
Has an `hjkl` "module", which makes `,` a prefix, `;` a modifier,
`,m` a layout switcher, and `,n` a Compose key.
Also has a cyrillic variant.

Is intended to be intuitive after QWERTY.
International/Dvorak/etc. variants almost aren't tested.

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
xkbcomp -I"path/to/qwaf/xkb" path/to/xkb/file $DISPLAY
```
To launch it at login, put the above in, say, `~/xkb.sh` file,
and add the `sh ~/xkb.sh` to autostart
(by putting this into `~/.xinitrc`, or tweaking desktop settings).

Bugs
----
Shift-selection with keys accessible through `;` does not work in MonoDevelop and Java apps.
The workaround is active by default, but has problems under Xserver 1.18.1 - 1.18.4.
If you are assembling your own `.xkb` file, check the output of `X -version`.
To disable the workaround, add `hjkl(lv5)` to `xkb_symbols`.

As the `xkbcomp` cannot distinguish between system and non-system includes,
all files under `xkb/` have "odd"/unique names.

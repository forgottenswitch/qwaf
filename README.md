QWAF
====

Latin/Cyrillic keyboard layout trying to be similar to Qwerty.
Works in X11 and Linux console.

The `hjkl` "module" makes `,` a prefix, `;` a modifier,
`,m` a layout switcher, and `,n` a Compose key.

  <img src="pic/qwaf.png" alt="Qwaf lv1" width="800" />

AltGr level, accesible with Comma:
  <img src="pic/qwaf-lv3.png" alt="Qwaf lv3" width="800" />

Second AltGr level, accessible with Semicolon:
  <img src="pic/qwaf-lv5.png" alt="Qwaf lv5" width="800" />

Cyrillic variant:
  <img src="pic/ru_intl.png" alt="Cyrillic lv1" width="800" />
  <img src="pic/ru_intl-lv3.png" alt="Cyrillic lv3" width="800" />

International/Dvorak/etc. variants almost aren't tested.

Building
--------
Run:
```
make
```
It will download X11 files into `fetch/`, and generate layouts into `gen/`.

Running in X11 (i.e. XKB)
-------------------------
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

To install (for the current user), put the above in a file, like `~/xkb.sh`
and add the `sh ~/xkb.sh` to autostart
(by putting this into `~/.xinitrc`, or tweaking desktop settings).

Running in Linux console
------------------------
```sh
make
sudo loadkeys gen/linux_console/qwaf_us.map
```
Note: to see Compose combinations, run `dumpkeys | grep --binary-files=text ^compose`

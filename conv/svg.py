import os
import re

name = "svg"

def convert(debug, outdir, keydefs, layouts, partials):
    print(layouts[0].compiled_keys)

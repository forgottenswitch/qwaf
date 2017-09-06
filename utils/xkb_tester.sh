#!/bin/sh

# exit on error
set -e

example_numbers="$(
  awk '
    /^[ 	]*[a-zA-Z0-9_]/ { n += 1; print n; }
  ' examples/xkb_examples
)"

for n in $example_numbers ; do
  echo
  echo "Running example $n ..."
  COMPILE_ONLY=1 examples/run_xkb_example.sh "$n"
done

echo
echo "All done, examples do compile."
echo

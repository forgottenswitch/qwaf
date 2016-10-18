#!/bin/sh

PROG="$0"

usage() {
  echo "Usage: $PROG [N]"
  echo " Run N-th example."
}

for arg ; do
  if test _"${arg#-}" != _"$arg" ; then
    usage
    exit
  fi
done

arg1="$1"

thisfile=$(readlink -e "$PROG")
thisdir="${thisfile%/*}"
this_updir="${thisdir%/*}"

filelist=""
for f in "$thisdir"/*.xkb ; do
  filelist="$filelist
$f"
done
filelist="${filelist#
}"

n="$1"

if test -z "$n" ; then
  echo "$filelist" | nl
  exit
fi

nth=$(echo "$filelist" | head -n "$((n))" | tail -n 1)

echo_and_run() {
  echo "$@"
  "$@"
}

echo_and_run xkbcomp "-I${this_updir}/xkb" "$nth" $DISPLAY

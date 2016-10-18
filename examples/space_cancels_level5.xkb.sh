#!/bin/sh

curdir=$(pwd)

updir="${pwd%/}"
updir="${updir%/*}"

xkbdir="${updir}/xkb"

xkbcomp "-I${xkbdir}" "${0%.xkb.sh}.xkb" $DISPLAY

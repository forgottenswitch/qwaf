#!/bin/sh

PROG="$0"

usage() {
  echo "Usage: $PROG [N]"
  echo " Run N-th example, or print them."
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

paragraph_count_awk='
  BEGIN { paragraph_n = 1; paragraph_started = 0; }
  /^[/]/ {}
  /^[ \t]*[^ \t]/ {
    paragraph_started = 1;
  }
  /^[ \t]*$/ {
    if (paragraph_started) {
      paragraph_n += 1;
      paragraph_started = 0;
    }
  }
'

if test -z "$arg1" ; then
  cat "${thisdir}/xkb_examples" | awk '
  '"$paragraph_count_awk"'
  BEGIN { paragraph_n_printed = 0; }
  /^[ \t]*[^ \t]/ {
    if (!paragraph_n_printed) {
      printf "  " paragraph_n ".";
      paragraph_n_printed = 1;
    }
  }
  /^[ \t]*$/ {
    paragraph_n_printed = 0;
  }
  { print "\t" $0; }
'
  exit
fi

nth_src=$(cat "${thisdir}/xkb_examples" | awk '
  '"$paragraph_count_awk"'
  /^[ \t]*[^/ \t]/ {
    if (paragraph_n == '"$((arg1))"') {
      print $0
      exit;
    }
  }
')

if test -z "$nth_src" ; then
  echo "Error: empty $((arg))-th example (wrong N ?)."
  exit 1
fi

xserver_handles_redirs=y
if X -version 2>&1 | grep -q "1.18.[1234]" ; then
  xserver_handles_redirs=n
fi

temp_xkb=$(mktemp)
cp "${thisdir}/qwaf_hjkl.xkb" "$temp_xkb"
sed -i -e "s/hjkl(qwaf)+ctrl(nocaps)/$nth_src/" "$temp_xkb"

# For Xorg 1.18.1 - 1.18.4, add "+hjkl(lv5)" to xkb_symbols
if test _"$xserver_handles_redirs" != _y ; then
  hjkl_tail="+hjkl(lv5)"
  for lv in 2 3 4; do
    if grep -q "xkb_symbols.*:$lv" "$temp_xkb" ; then
      hjkl_tail="${hjkl_tail}+hjkl(lv5):$lv"
    fi
  done
  sed -i -e 's/\(.*xkb_symbols.*\)\(\"[^"]*$\)/\1+hjkl(redirs)'"$hjkl_tail"'\2/' "$temp_xkb"
fi

echo_and_run() {
  echo "$@"
  "$@"
}

echo
echo "$temp_xkb:"
echo "---"
cat "$temp_xkb"
echo "---"
echo
echo_and_run xkbcomp "-I${this_updir}/gen/xkb" "$temp_xkb" $DISPLAY
rm "$temp_xkb"

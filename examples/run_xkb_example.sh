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

temp_xkb_src="$(mktemp)"
temp_xkb_out="$(mktemp)"
cp "${thisdir}/qwaf_hjkl.xkb" "$temp_xkb_src"
sed -i -e "s/qwaf_layouts(qwaf)+ctrl(nocaps)/$nth_src/" "$temp_xkb_src"

echo_and_run() {
  echo "$@"
  "$@"
}

silent_ok() {
  "$@" 2>/dev/null || true
}

run_xkbcomp() {
  if test "$((COMPILE_ONLY))" -eq 0 ; then
    echo_and_run xkbcomp "$@" "$DISPLAY"
  else
    echo_and_run xkbcomp "$@" -xkb -o "$temp_xkb_out"
  fi

  xkb_out="$( silent_ok cat "$temp_xkb_out" )"

  # xkbcomp exits 0 even when failing to compile;
  # so examine the output file to check whether the
  # compilation was successfull
  if test -z "$xkb_out" ; then
    return 1
  fi
  return 0
}

echo
echo "$temp_xkb_src:"
echo "---"
cat "$temp_xkb_src"
echo "---"
echo

run_xkbcomp "-I${this_updir}/gen/xkb" "$temp_xkb_src"
xkbcomp_status="$?"

silent_ok rm "$temp_xkb_src"
silent_ok rm "$temp_xkb_out"

exit "$xkbcomp_status"

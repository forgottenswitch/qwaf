#!/bin/sh

# exit on error
set -e

generated_files_dir="$1" ; shift
rules_to_add="$1" ; shift

generated_xkb_dir="$generated_files_dir"/xkb

xkb_subdirs="compat symbols types"

xkb_dotdir="$HOME"/.xkb
xkb_default_rules="evdev"

fatal() {
  echo "error:" "$@" >&2
  exit 1
}

confirm() {
  fmt="$1" ; shift

  while true ; do
    printf "$fmt [Y/n]> " "$@"
    read x
    if test _"$x" = _"" -o _"$x" = _y -o _"$x" = _Y ; then
      break
    elif test _"$x" = _"n" -o _"$x" = _N ; then
      exit 1
    fi
  done
}

find_system_rules_file() {
  file_to_find="$xkb_default_rules"
  echo "Searching for xkeyboard-config system rules file '$file_to_find':"

  for dir in \
    "/usr/share/X11*" \
    "/usr/X11*" \
    "/usr/local/share/X11*" \
    "/usr/local/X11*" \
    "/usr/pkg/share/X11*" \
    "/usr/pkg" \
    "/usr"
  do
    echo "  in $dir ..."

    path="$( eval "find $dir -path '*/rules/$file_to_find' 2>/dev/null || true" )"

    if test ! -z "$path" ; then
      system_rules="$( echo "$path" | head -n1 )"

      echo "  Found: ${system_rules}"
      return
    fi
  done

  echo
  echo "  Not found"
  fatal "Cannot find the '$file_to_find' rules file from xkeyboard-config."
}

create_home_directories() {
  for xkb_subdir in rules $xkb_subdirs ; do
    dir_to_create="$xkb_dotdir"/"$xkb_subdir"
    if test ! -d "$dir_to_create" ; then
      echo "Creating directory $dir_to_create ..."
      mkdir -p "$dir_to_create"
    fi
  done
}

put_rules_file_to_home() {
  file_to_write="$xkb_dotdir"/rules/"$xkb_default_rules"_qwaf

  confirm "Would write %s, continue?" "$file_to_write"

  echo " Copying $system_rules into $file_to_write ..."
  cp "$system_rules" "$file_to_write"

  echo " Appending rules to $file_to_write ..."
  echo >> "$file_to_write"
  cat "$rules_to_add" >> "$file_to_write"
}

symlink_generated_files() {
  confirm "Would symlink files from %s/ into %s/, continue?" "$generated_xkb_dir" "$xkb_dotdir"

  for xkb_subdir in $xkb_subdirs ; do
    for xkb_file in "$generated_xkb_dir"/"$xkb_subdir"/* ; do
      filename="${xkb_file##*/}"
      dest_file="$xkb_dotdir"/"$xkb_subdir"/"$filename"
      targ_file="$( realpath --relative-to="$xkb_dotdir"/"$xkb_subdir" "$xkb_file" )"
      ln -s -v -f "$targ_file" "$dest_file"
    done
  done
}

find_system_rules_file
create_home_directories
put_rules_file_to_home
symlink_generated_files

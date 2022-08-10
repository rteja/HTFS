#!/usr/bin/env bash


_tagfs_completions()
{
  if [ "${#COMP_WORDS[@]}" != "2" ]; then
	return
  fi

  COMPREPLY=($(compgen -W "init lstags addtags linktags addresource tagresource lsresources help" "${COMP_WORDS[1]}"))
}

complete -F _tagfs_completions tagfs.py


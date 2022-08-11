#!/usr/bin/env bash



_tagfs_completions()
{
  if [ "${#COMP_WORDS[@]}" == 2 ]; then
    COMPREPLY=($(compgen -W "init lstags addtags linktags addresource tagresource lsresources help" "${COMP_WORDS[1]}"))
  fi

  if [ "${#COMP_WORDS[@]}" == 3 ]; then

    if [ "${COMP_WORDS[1]}" == "addresource" ]; then
      COMPREPLY=($(compgen -W "$(ls)" "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "tagresource" ]; then
      COMPREPLY=($(compgen -W "$(ls)" "${COMP_WORDS[2]}"))
    fi
  fi

  if [ "${#COMP_WORDS[@]}" == 4 ]; then
    if [ "${COMP_WORDS[1]}" == "tagresource" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[3]}"))
    fi
  fi
}

complete -F _tagfs_completions tagfs
complete -F _tagfs_completions tagfs.py


#!/usr/bin/env bash

_tagfs_completions()
{
  if [ "${#COMP_WORDS[@]}" == "2" ]; then
    COMPREPLY=($(compgen -W "init getboundary lstags addtags renametag linktags addresource tagresource untagresource lsresources rmresource mvresource getresourcetags rmresourcetags help" "${COMP_WORDS[1]}"))
  fi

  if [ "${#COMP_WORDS[@]}" == "3" ]; then

    if [ "${COMP_WORDS[1]}" == "addresource" ]; then
      COMPREPLY=($(compgen -f -- "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "tagresource" ]; then
      COMPREPLY=($(compgen -f -- "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "untagresource" ]; then
      COMPREPLY=($(compgen -f -- "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "mvresource" ]; then
      COMPREPLY=($(compgen -f -- "${COMP_WORDS[2]}"))
    fi
    
    if [ "${COMP_WORDS[1]}" == "rmresource" ]; then
      COMPREPLY=($(compgen -f -- "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "getresourcetags" ]; then
      COMPREPLY=($(compgen -f -- "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "rmresourcetags" ]; then
      COMPREPLY=($(compgen -f -- "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "lstags" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "lsresources" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[2]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "renametag" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[2]}"))
    fi
    
    if [ "${COMP_WORDS[1]}" == "linktags" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[2]}"))
    fi
    
  fi

  if [ "${#COMP_WORDS[@]}" == "4" ]; then
    if [ "${COMP_WORDS[1]}" == "tagresource" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[3]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "untagresource" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[3]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "linktags" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[3]}"))
    fi
  fi

  if [ ${#COMP_WORDS[@]} -gt 4 ]; then
    if [ "${COMP_WORDS[1]}" == "tagresource" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[${#COMP_WORDS[@]} - 1]}"))
    fi

    if [ "${COMP_WORDS[1]}" == "untagresource" ]; then
      COMPREPLY=($(compgen -W "$(tagfs lstags)" "${COMP_WORDS[${#COMP_WORDS[@]} - 1]}"))
    fi
  fi
}

complete -F _tagfs_completions tagfs
complete -F _tagfs_completions tagfs.py


#!/bin/bash

################################################################################
#                            walrus_completion.sh                              #
#   This script was coded by stakin.com.                                       #
#   If you encounter any bugs, please report them at:                          #
#   https://github.com/StakinOfficial/walrus-completion/issues                     #
#                                                                              #
#   Licensed under the MIT License.                                            #
#                                                                              #
################################################################################


_generate_walrus_completions() {
    local cur prev opts program
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    program="${COMP_WORDS[0]}"  # Dynamic naming

    # Identification
    local command subcommand subsubcommand
    for ((i = 1; i < COMP_CWORD; i++)); do
        if [[ "${COMP_WORDS[i]}" != -* ]]; then
            if [[ -z "$command" ]]; then
                command="${COMP_WORDS[i]}"
            elif [[ -z "$subcommand" ]]; then
                subcommand="${COMP_WORDS[i]}"
            else
                subsubcommand="${COMP_WORDS[i]}"
                break
            fi
        fi
    done

    # Parsing
    local help_output
    if [[ -n "$subsubcommand" ]]; then
        help_output=$("${program}" "$command" "$subcommand" "$subsubcommand" --help 2>/dev/null)
    elif [[ -n "$subcommand" ]]; then
        help_output=$("${program}" "$command" "$subcommand" --help 2>/dev/null)
    elif [[ -n "$command" ]]; then
        help_output=$("${program}" "$command" --help 2>/dev/null)
    else
        help_output=$("${program}" --help 2>/dev/null)
    fi

    # Extraction
    opts=$(echo "$help_output" | awk '/Commands:/,/^$/ {if (!/:/ && !/^$/ && $1) print $1}')
    opts+=" $(echo "$help_output" | grep -oE '\-\-[a-zA-Z0-9\-]+' | sort -u)"

    # Dups removal
    opts=$(echo "$opts" | tr ' ' '\n' | awk '!seen[$0]++' | tr '\n' ' ')

    # Finally complete based on the current word
    COMPREPLY=($(compgen -W "${opts}" -- "${cur}"))
}

# Whitelist commands
commands=(
    walrus
)

for cmd in "${commands[@]}"; do
    complete -F _generate_walrus_completions "$cmd"
done
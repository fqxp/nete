#compdef nete

function _complete_command {
    local -a commands=( \
        cat:"Print note" \
        edit:"Edit note" \
        ls:"List notes" \
        new:"Create note" \
        repl:"Run REPL" \
        rm:"Remove note" \
        )
    _describe 'commands' commands
}

function _complete_note_id {
    local -a note_ids
    nete ls | while read note_id title ; do
        note_ids+=($note_id:"$title")
    done
    _describe 'note IDs' note_ids
}

function _nete-cat {
    _arguments -s \
        '*::arg:_complete_note_id'
}

function _nete-edit {
    _arguments -s \
        '1::arg:_complete_note_id'
}

function _nete-ls {
    _arguments \
        '-l[list details]' \
        '--long[list details]'
}

function _nete-new {
    _message -r 'Please provide a title for the new note'
}

function _nete-repl {
    _message -r 'No options'
}

function _nete-rm {
    _arguments -s \
        '*::arg:_complete_note_id'
}

function _nete {
    local line
    typeset -A opt_args

    _arguments -C \
        '-D[enable debug output]' \
        '-V[print version]' \
        '1::command:_complete_command' \
        '*::arg:->args'

    [ -n "$line[1]" ] && "_nete-${line[1]}"
}

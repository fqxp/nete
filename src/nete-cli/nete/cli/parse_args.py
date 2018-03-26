import argparse
import pkg_resources

__version__ = pkg_resources.get_distribution('nete-cli').version


def parse_args(config):
    parser = argparse.ArgumentParser()

    parser.add_argument('-D', '--debug',
                        action='store_true',
                        help='Enable debug output')
    parser.add_argument('-V', '--version',
                        action='version',
                        help='Print version and exit',
                        version=__version__)

    subparsers = parser.add_subparsers(help='Commands')

    cat_parser = subparsers.add_parser('cat',
                                       help='Print note to stdout')
    cat_parser.add_argument('note_ids', type=str, nargs='+',
                            help='Note IDs')
    cat_parser.set_defaults(cmd='cat')
    cat_parser.set_defaults(options=options(cat_parser))

    edit_parser = subparsers.add_parser('edit', help='Edit note')
    edit_parser.add_argument('note_id', type=str, help='Note ID')
    edit_parser.set_defaults(cmd='edit')
    edit_parser.set_defaults(options=options(edit_parser))

    ls_parser = subparsers.add_parser('ls', help='List notes')
    ls_parser.set_defaults(cmd='ls')
    ls_parser.set_defaults(options=options(ls_parser))

    new_parser = subparsers.add_parser('new', help='Create a note')
    new_parser.add_argument('title', type=str, help='Note title')
    new_parser.set_defaults(cmd='new')
    new_parser.set_defaults(options=options(new_parser))

    repl_parser = subparsers.add_parser('repl', help='Run REPL')
    repl_parser.set_defaults(cmd='repl')
    repl_parser.set_defaults(options=options(repl_parser))

    repl_parser = subparsers.add_parser('repl', help='Run REPL')
    repl_parser.set_defaults(cmd='repl')

    rm_parser = subparsers.add_parser('rm', help='Delete notes')
    rm_parser.add_argument('note_ids', type=str, nargs='+',
                           help='Note IDs')
    rm_parser.set_defaults(cmd='rm')
    rm_parser.set_defaults(options=options(rm_parser))

    return parser.parse_args()


def options(parser):
    return [
        action.dest
        for action in parser._actions
        if action.dest != 'help'
    ]

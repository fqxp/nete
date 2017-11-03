from .nete_client import NeteClient
from .repl import Repl


def main():
    nete_client = NeteClient('http://127.0.0.1:8080')
    repl = Repl(nete_client)
    try:
        repl.cmdloop()
    except KeyboardInterrupt:
        pass

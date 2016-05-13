from restler import Restler

import code

try:
    import readline
except ImportError:
    pass
else:
    # import rlcompleter
    # readline.set_completer(rlcompleter.Completer(imported_objects).complete)
    readline.parse_and_bind("tab:complete")

lo = Restler('http://localhost:9000/')

code.interact('''
preimported: Restler
predefined: lo -> Restler('localhost')

''', local=locals())

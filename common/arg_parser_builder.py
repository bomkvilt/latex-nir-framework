from __future__ import annotations
import argparse
from typing import Any


class ArgParserBuilder:
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._subcommands = None

    # addCommand 
    def addCommand(self, cmd: str, help: str = None) -> ArgParserBuilder:
        subparsers = self._getSubcommands()
        subbuilder = ArgParserBuilder()
        subbuilder._parser = subparsers.add_parser(cmd, help=help)
        return subbuilder

    # addArgument 
    def addArgument(self, argname: str, *,
        help:     str       = None,
        required: bool      = True,
        default:  Any       = None,
        choices:  list[str] = None,
    ):
        kwargs = {}
        if (not required):
            kwargs['required'] = required
            kwargs['default'] = default
        
        self._parser.add_argument(argname, help=help, choices=choices, **kwargs)
    
    def addFlag(self, argname: str, *, 
        on_action: bool = True, 
        help:      str  = None,
        hasNo:     bool = True,
    ):
        kwargs = {}
        if hasNo:
            if (on_action == True):
                kwargs['action']  = "store_true"
                kwargs['default'] = False
            else:
                kwargs['action']  = "store_false"
                kwargs['default'] = True
        else:
            kwargs['action']  = argparse.BooleanOptionalAction
            kwargs['default'] = True

        self._parser.add_argument(argname, help=help, **kwargs)

    # addHandler assigns a handler to the underprocessing command
    def addHandler(self, handler):
        self._parser.set_defaults(callback=handler)

    # parseArgs
    def parseArgs(self, args):
        ns = self._parser.parse_args(args)
        if 'callback' in ns:
            ns.callback(ns)

    # private:

    def _getSubcommands(self):
        if self._subcommands == None:
            self._subcommands = self._parser.add_subparsers()
        return self._subcommands

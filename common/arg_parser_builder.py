from __future__ import annotations
import argparse


class ArgParserBuilder:
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._subcommands = None

    # addCommand 
    def addCommand(self, cmd:str, help:str = None) -> ArgParserBuilder:
        subparsers = self._getSubcommands()
        subbuilder = ArgParserBuilder()
        subbuilder._parser = subparsers.add_parser(cmd, help=help)
        return subbuilder

    # addArgument 
    def addArgument(self, arg:str, 
        help:str      = None,
        required:bool = True,
        default       = None,
    ):
        kwargs = {}
        if (not required):
            kwargs['required'] = required
            kwargs['default' ] = default
        self._parser.add_argument(arg, help=help, **kwargs)

    # addHandler assigns a handler to the underprocessing command
    def addHandler(self, handler):
        self._parser.set_defaults(callback=handler)

    # parseArgs
    def parseArgs(self, args):
        args = self._parser.parse_args(args)
        if 'callback' in args:
            args.callback(args)

# private:

    def _getSubcommands(self):
        if self._subcommands == None:
            self._subcommands = self._parser.add_subparsers()
        return self._subcommands

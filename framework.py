from modules.Type2TEX.module  import Type2TEX
from modules.generator.module import Generator
from os import path
import argparse


class Framework:
    def __init__(self,
        sections_root:str  = "sections",  # 
        build_path:str     = "build/TeX", #
        proj_path:str      = ".",         #
        src_fig_name:str   = "fig",       #
        src_eqs_name:str   = "eqs",       #
    ):
        self._module_root   = path.dirname(path.realpath(__file__))
        self._sections_root = sections_root
        self._modules       = {
            "type2tex" : Type2TEX (build_path=build_path, proj_path=proj_path),
            "generator": Generator(build_path=build_path, proj_path=proj_path,
                src_fig_name=src_fig_name,
                src_eqs_name=src_eqs_name,
            ),
        }
        self._argparser = self._create_parser_()

    def getParser(self) -> argparse.ArgumentParser: 
        return self._argparser

    def processArgs(self):
        args = self._argparser.parse_args()
        if args.callback:
            args.callback(args)

# private:

    def _create_parser_(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        commands = parser.add_subparsers()
        for name, module in self._modules.items():
            subparser = commands.add_parser(name)
            callback  = module.assignToArgParser(subparser)
            subparser.set_defaults(callback=callback)
        return parser
        

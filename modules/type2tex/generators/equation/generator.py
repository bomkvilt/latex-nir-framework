from jinja2.environment import Template
from jinja2.loaders import BaseLoader
from ...equationInfo import FEquationInfo

from jinja2 import Environment

import os
import re



class EquationsGenerator:

    def __init__(self) -> None:
        # generator source file directory
        self._root = os.path.dirname(os.path.realpath(__file__))

        escpB2EB = [
            (r'{#(?=\d)', r'<<<1# >>>', r'\{\#'),
            (r'{{!'     , r'<<<1__>>>', r'{{'),
            (r'!}}'     , r'<<<2__>>>', r'}}'),
            (r'{%'      , r'<<<1_ >>>', r'{%'),
            (r'%}'      , r'<<<2_ >>>', r'%}'),
        ]
        escpB2E = dict((v1, v2) for v1, v2, v3 in escpB2EB)
        escpE2B = dict((v2, v3) for v1, v2, v3 in escpB2EB)
        escpB = {
            r'{': r'\\{',
            r'}': r'\\}',
        }
        unescB = { 
            # to : from - the fromat is taken to simplify unescape-patterns generation code
            r'{#' : r'\{\\#'
        }
        # template cleanup patterns
        self._cleanupPatterns  = [(re.compile(x), y) for x, y in (escpB2E | escpB | escpE2B).items()]
        self._unescapePatterns = [(re.compile(y), x) for x, y in (escpB | unescB).items()]

        # load template
        templatepath = f'{self._root}/equation.templ.tex'
        with open(templatepath) as file:
            template = file.read()
            template = self._processTemplate(template)
        self._templateUpdateTime = os.path.getmtime(templatepath)
        loader = Environment(loader=BaseLoader())
        self._template = loader.from_string(template)


    def Generate(self, eqinfo: FEquationInfo) -> None:
        outdata = self._render(eqinfo)
        return outdata

    def LastUpdateTime(self) -> float:
        return self._templateUpdateTime

    # protected:

    def _render(self, eqinfo: FEquationInfo) -> str:
        vars    = self._generateVars(eqinfo)
        outdata = self._template.render(vars = vars)
        outdata = self._unescapeOutput(outdata)
        return outdata

    def _generateVars(self, eqinfo: FEquationInfo) -> dict[str, str]:
        return {
            'equations': eqinfo.equations,
            'varexpls' : eqinfo.varexpls,
        }

    def _unescapeOutput(self, outdata: str) -> str:
        for pattern, repl in self._unescapePatterns:
            outdata = pattern.sub(repl, outdata)
        return outdata

    ## _processTemplate escapes '{' and '}' braces in specific cases
    def _processTemplate(self, template: str) -> str:
        for pattern, repl in self._cleanupPatterns:
            template = pattern.sub(repl, template)
        return template


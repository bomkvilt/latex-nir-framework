from ...equationInfo import FEquationInfo
from ....includes import Singleton

from jinja2.loaders import BaseLoader
from jinja2 import Environment

import os
import re



class _texEscaper(metaclass = Singleton):
    def __init__(self) -> None:
        # typed -> escaped -> final
        escapeTemplateSymbols = [
            # escape commentaries
            (r'{#!', r'<<<1# >>>', r'{#'),
            (r'!#}', r'<<<2# >>>', r'#}'),
            # escape expression blocks
            (r'{{!', r'<<<1__>>>', r'{{'),
            (r'!}}', r'<<<2__>>>', r'}}'),
            # escape statement blocks
            # \note '{!' & '!}' were invented to keep latex syntax in
            #   template documents in single-row constryctions since 
            #   '{% ..' get parsed as text('{') + comment('% ..')
            (r'{%' , r'<<<1_ >>>', r'{%'),
            (r'{!' , r'<<<1_ >>>', r'{%'),
            (r'!}' , r'<<<2_ >>>', r'%}'),
            (r'%}' , r'<<<2_ >>>', r'%}'),
        ]

        # typed -> escaped -> final
        escapeTextSymbols = [
            (r'{', r':::1 1:::', r'{'),
            (r'}', r':::1 2:::', r'}'),
        ]

        # generate transformation list that will convert text to a state that can be used with
        # a template processor: escape templates -> escape rest text -> unescape templates 
        escapeRules = list[tuple[re.Pattern, str]]()
        for v1, v2, v3 in escapeTemplateSymbols:
            escapeRules.append((re.compile(v1), v2))
        for v1, v2, v3 in escapeTextSymbols:
            escapeRules.append((re.compile(v1), v2))
        for v1, v2, v3 in escapeTemplateSymbols:
            escapeRules.append((re.compile(v2), v3))

        # generate transformation list that will convert 
        # escaped text's state to a final one
        unescapeRules = list[tuple[re.Pattern, str]]()
        for v1, v2, v3 in escapeTextSymbols:
            unescapeRules.append((re.compile(v2), v3))
        
        self._escapeRules = escapeRules
        self._unescapeRules = unescapeRules


    def EscapeToPattern(self, text: str) -> str:
        for regex, repl in self._escapeRules:
            text = regex.sub(repl, text)
        return text
    
    def UnescapeRender(self, text: str) -> str:
        for regex, repl in self._unescapeRules:
            text = regex.sub(repl, text)
        return text



class EquationsGenerator(metaclass = Singleton):

    def __init__(self) -> None:
        # init environment and tools
        self._root = os.path.dirname(os.path.realpath(__file__))
        self._templatepath = f'{self._root}/equation.templ.tex'

        # cash template's last modify time
        self._templateUpdateTime = os.path.getmtime(self._templatepath)

    def Generate(self, eqinfo: FEquationInfo) -> None:
        outdata = self._render(eqinfo)
        return outdata

    # this function returns template's last modification time
    # \note this information is requred to decide if rerender is needed or not in top-level logic
    # \note if render order is taken the render will be done independently from the values
    def LastUpdateTime(self) -> float:
        return self._templateUpdateTime

    # protected:

    def _loadTemplateDriver(self):
        if (hasattr(self, '_template')):
            return

        self._escaper = _texEscaper()

        # load template file
        with open(self._templatepath) as file:
            template = file.read()
            template = self._escaper.EscapeToPattern(template)

        # create a template driver
        loader = Environment(loader = BaseLoader())
        self._template = loader.from_string(template)

    def _render(self, eqinfo: FEquationInfo) -> str:
        self._loadTemplateDriver()
        vars    = self._generateVars(eqinfo)
        outdata = self._template.render(vars = vars)
        outdata = self._escaper.UnescapeRender(outdata)
        return outdata

    def _generateVars(self, eqinfo: FEquationInfo) -> dict[str, str]:
        return {
            'equations': eqinfo.equations,
            'varexpls' : eqinfo.varexpls,
        }

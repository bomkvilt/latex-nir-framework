from .generators.equation.generator import EquationsGenerator
from .classes.texVarexplParser import TexVarexplParser, VariableExplanation
from .classes.texEQLabelParser import EquationData, TexEQLabelParser
from .equationInfo import FEquationInfo

import typing
import re



class T2TBackend:
    def __init__(self) -> None:
        self._processor = _texProcessor()

    def ProcessMMLTree(self, mmltree: typing.Any) -> str:
        mmltree = self._processMML(mmltree)
        textext = self._convertMML(mmltree)
        texdata = self._processor.ProcessEquation(textext)
        return texdata

    def LastUpdateTime(self) -> float:
        return self._processor.LastUpdateTime()

    # protected:

    def _processMML(self, mmltree: typing.Any) -> typing.Any:
        return mmltree

    def _convertMML(self, mmltree: typing.Any) -> str:
        return str(mmltree).replace('$', '')



class _texProcessor:
    def __init__(self) -> None:
        self._varexplParser = TexVarexplParser()
        self._EQLabelParser = TexEQLabelParser()
        self._EQGenerator   = EquationsGenerator()

    def ProcessEquation(self, equation: str) -> str:
        # process passed equation
        equation  = self._normalizeEquation(equation)
        equation  = self._dropCommentaries(equation)
        varexpls  = self._varexplParser.ExtractExplanations(equation)
        equation  = self._varexplParser.DropExplanations(equation)
        equations = self._EQLabelParser.ExtractEquations(equation)
        # render .tex code
        return self._renderTeX(varexpls, equations)
        
    def LastUpdateTime(self) -> float:
        t0 = self._EQGenerator.LastUpdateTime()
        return max([t0])

    # protected:

    def _normalizeEquation(self, equation: str) -> str:
        for seq in ['\u200b', '$' , '\r']:
            equation = equation.replace(seq, '')
        for key, val in {
            r'\frac': r'\dfrac', # don't reduce font size for fractoin's memebers
            '\u00A0': ' ', # replace non-breaking space with a common space
        }.items():
            equation = equation.replace(key, val)
        return equation

    def _dropCommentaries(self, equation: str) -> str:
        pattern  = re.compile( '(' r'\\text{#.*?}(?:\\text{.*?})*(?:\\\\)?' ')')
        equation = pattern.sub('', equation)
        return equation

    def _renderTeX(self, varexpls: list[VariableExplanation], equations: list[EquationData]) -> str:
        eqinfo = FEquationInfo()
        eqinfo.equations = equations
        eqinfo.varexpls  = varexpls
        self._deduceStretch(equations)
        return self._EQGenerator.Generate(eqinfo)

    @staticmethod
    def _deduceStretch(equations: list[EquationData]) -> float:
        for eqdata in equations:
            bUseDouble = r'\dfrac' in eqdata.data
            eqdata.stretch = 2. if bUseDouble else 1.

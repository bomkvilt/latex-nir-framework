from ...includes import Singleton
from .baseTexParser import BaseTexParser

import string
import re



class _numToString(metaclass = Singleton):
    def __init__(self) -> None:
        self.base = len(string.ascii_lowercase)
        self.num2letter = dict(zip(
            range(self.base),
            string.ascii_lowercase
        ))
    
    # 1  -> a
    # 26 -> z
    # 27 -> aa
    def convert(self, num: int) -> str:
        assert(num > 0)

        ans = ''
        while num > 0:
            rem = (self.base + num % self.base - 1) % self.base
            num = num // self.base
            ans = self.num2letter[rem] + ans
        return ans


class EquationData:
    def __init__(self) -> None:
        self.label:str
        self.data:str
        self.id:str


class _arrayUnwrapper(BaseTexParser):
    def __init__(self) -> None:
        super().__init__()
        # marckup patterns
        openseq  = r'^\s*'
        openkey  = r'\\begin{array}{.*?}' # \1
        closekey = r'\\end{array}'        # \2
        closeseq = r'\s*$'                # \3
        valuekey = '({})'.format(self.TEXT(r'.*?'))
        # compile regular expression
        self._pattern = openseq + openkey + valuekey + closekey + closeseq
        self._matcher = re.compile(self._pattern)

    def UnwrapArray(self, equation:str) -> str:
        return re.sub(self._pattern, r'\1', equation)



class TexEQLabelParser(BaseTexParser):
    def __init__(self) -> None:
        super().__init__()
        # marckup patterns
        openkey  = r'\\left\\{\\left\\{'
        closekey = r'\\right\\}\\right\\}'
        valuekey = '({})'.format(self.TEXT(r'.*?'))
        # compile a regular expression
        self._pattern = f'{openkey + valuekey + closekey}' + r'(?:\\\\)?'
        self._matcher = re.compile(self._pattern)
        # subcompilers
        self._arrayUnwrapper = _arrayUnwrapper()

    def ExtractEquations(self, equation: str) -> list[EquationData]:
        entery = self._arrayUnwrapper.UnwrapArray(equation)
        # if the equation is not an array it can not have
        # markup symbols (we assume the symbols are 1st level ones)
        if (entery == equation):
            eqdata = EquationData()
            eqdata.label = ''
            eqdata.data  = equation
            eqdata.id    = 'a'
            return [eqdata]
        return self._extractEquation(entery)        

    def _extractEquation(self, equation: str) -> list[EquationData]:
        # extract labels and split equation
        cursor = 0
        equations = list[EquationData]()
        for match in self._matcher.finditer(equation):
            i0, i1 = match.regs[0]
            # save previous data block
            if (len(equations) > 0):
                eqdata      = equations[-1]
                eqdata.data = equation[cursor:i0]
            cursor = i1
            # create a new block
            eqdata       = EquationData()
            eqdata.label = match.group(1)
            equations.append(eqdata)
        # if the equation has no labels
        if (len(equations) == 0):
            eqdata = EquationData()
            eqdata.label = ''
            equations.append(eqdata)
        # flush rest substrings
        eqdata      = equations[-1]
        eqdata.data = equation[cursor:]
        return self._addIDs(equations)

    def _addIDs(self, equations: list[EquationData]) -> list[EquationData]:
        generator = _numToString()
        counter   = 1
        for eqdata in equations:
            eqdata.id = generator.convert(counter)
            counter  += 1
        return equations

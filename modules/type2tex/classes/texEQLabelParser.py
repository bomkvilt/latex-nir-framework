from .baseTexParser import BaseTexParser

import re



class EquationData:
    def __init__(self) -> None:
        self.label:str
        self.data:str


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
            return [eqdata]
        return self._extractEquation(entery)        

    def _extractEquation(self, equation: str) -> list[EquationData]:
        # extract labels and split equation
        coursor = 0
        equations = list[EquationData]()
        for match in self._matcher.finditer(equation):
            i0, i1 = match.regs[0]
            # save previous data block
            if (len(equations) > 0):
                eqdata      = equations[-1]
                eqdata.data = equation[coursor:i0]
            coursor = i1
            # create a new block
            eqdata       = EquationData()
            eqdata.label = match.group(1)
            equations.append(eqdata)
        # if equation have no labels
        if (len(equations) == 0):
            eqdata = EquationData()
            eqdata.label = ''
            equations.append(eqdata)
        # compleate last equation block
        eqdata      = equations[-1]
        eqdata.data = equation[coursor:]
        return equations

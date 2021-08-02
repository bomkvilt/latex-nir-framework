from .baseTexParser import BaseTexParser

import re



class VariableExplanation:
    def __init__(self) -> None:
        self.key:str
        self.val:str


class TexVarexplParser(BaseTexParser):
    def __init__(self) -> None:
        super().__init__()
        # marckup patterns
        openkey  = r'\\left\[\\left\['
        closekey = r'\\right]\\right]'
        splitkey = r';;'
        valuekey = '({})'.format(self.TEXT(r'.*?'))
        # compile a regular expression
        self._pattern = f'({openkey + valuekey + splitkey + valuekey + closekey})' + r'(?:\\\\)?'
        self._matcher = re.compile(self._pattern)

    ##
    # \brief ExtractExplanations scans LaTeX equation code for variable explanation patterns
    # \return found explanations
    def ExtractExplanations(self, equation:str) -> list[VariableExplanation]:
        # find explanations
        expls = list[VariableExplanation]()
        for match in self._matcher.finditer(equation):
            expl = VariableExplanation()
            expl.key = match.group(2)
            expl.val = match.group(3)
            expls.append(expl)
        return expls

    ##
    # \brief DropExplanations remove varexpl code from the equation
    # \return a sanitized string
    def DropExplanations(self, equation:str) -> str:
        # drop found code from the equation
        equation = re.sub(self._matcher, '', equation)
        return equation

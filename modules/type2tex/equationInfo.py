from .classes.texEQLabelParser import EquationData
from .classes.texVarexplParser import VariableExplanation



class FEquationInfo:
    def __init__(self) -> None:
        self.equations = list[EquationData]()
        self.varexpls  = list[VariableExplanation]()

from os   import path
from lxml import etree as ET
import json, re



### class that reads a raw .eps/none file and
#   converts it into a raw TeX code
class MMLFrontend:
    def __init__(self,
        mmltex_path:str = ":/mmltex/mmltex.xsl",  # path to mmltex directory
        tokens_path:str = ":/utiles/tokens.json", # path to extracted mml tokens
    ):
        self._module_root = path.dirname(path.realpath(__file__))
        self._mmltex_path = self._fixAbsPath(mmltex_path)
        self._tokens_path = self._fixAbsPath(tokens_path)
        self._tokens_list = self._loadMMLTokens()
    
    ### convert .eps/none entery into LaTeX code
    def ParseEquation(self, epsText:str) -> str:
        epsText = self._stanitizeEPS(epsText)
        mmlText = self._extractMML  (epsText)
        mmlText = self._sanitizeMML (mmlText)
        texText = self._convertToTeX(mmlText)
        return texText
    
# private: mml

    def _extractMML(self, epsText:str) -> str:
        mmlTexts = re.findall(r"(<math.*</math>)", epsText)
        if len(mmlTexts) != 1:
            raise RuntimeError('.eps files must have only one <math></math> block, but presented {}'.format(len(mmlTexts)))
        return mmlTexts[0]

    def _stanitizeEPS(self, epsText:str) -> str:
        epsText = epsText.replace('\r', '')
        epsText = epsText.replace('\n', '')
        epsText = epsText.replace('%' , '')
        return epsText

    def _sanitizeMML(self, mmlText:str) -> str:
        # Recover spaces betwean atributes
        # atr1="val1"atr2='val2' -> atr1="val1" atr2='val2'
        mmlText = re.sub(r"([^=])'(\w)", r"\1' \2", mmlText)
        mmlText = re.sub(r'([^=])"(\w)', r'\1" \2', mmlText)

        # Recover spaces betwean element names and thar atributes
        # \note: < name ...> allows to identify the block as fixed
        for token in self._tokens_list:
            mmlText = mmlText.replace('<' + token, '< ' + token + ' ')

        bSpacesFixed = False
        while not bSpacesFixed:
            mmlText1     = mmlText.replace('< ', '<').replace(' >', '>').replace('  ', ' ')
            bSpacesFixed = mmlText == mmlText1
            mmlText      = mmlText1
        
        return mmlText.replace('<math>', '<math xmlns="http://www.w3.org/1998/Math/MathML">')        

    def _convertToTeX(self, mmlText) -> str:
        try:
            xslt    = ET.parse(self._mmltex_path)
            mmlDom  = ET.fromstring(mmlText)
            mmlDom  = ET.XSLT(xslt)(mmlDom )
            texText = str(mmlDom).replace('$', '')
        except:
            print(mmlText)
            raise
        return texText

# private: utiles

    def _loadMMLTokens(self) -> list:
        tokens = json.load(open(self._tokens_path, 'r'))
        tokens = sorted(tokens, reverse=True)
        return tokens

    def _fixAbsPath(self, inPath:str) -> str:
        if inPath.startswith(':/'):
            inPath = path.join(self._module_root, inPath[2:])
        inPath = path.abspath(inPath)
        return inPath.replace('\\', '/')

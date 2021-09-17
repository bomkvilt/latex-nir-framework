from .settings import tokensPath, mmltexPath
from lxml import etree

import typing
import re
import json



## 
# \brief T2TFrontend is a class that parses specified .eps
# MathType equation file, converts it to an xml tree and applyes 
# transformation over the tree. The final result of the class'
# work is the MathML XML tree
class T2TFrontend:
    def __init__(self) -> None:
        # \brief load mml token list.
        # \note tokens must be rsorted to make out 'rm' and 'rmx' tags
        # so if the tags to check are are placed in 'rmx', 'rm' order
        # a source data will be recognized as it goes in an original file
        with open(tokensPath, 'r') as file:
            self._tokens = json.load(file)
            self._tokens = sorted(self._tokens, reverse = True)
            file.close()


    def ProcessEPSFile(self, path: str) -> typing.Any:
        with open(path, 'r') as file:
            rawdata = file.read()
            file.close()
        
        # pars raw data to extract fixed mml code
        rawdata = self._sanitizeEPS(rawdata)
        mmldata = self._extractMML(rawdata)
        mmltree = self._generateTree(mmldata)
        mmltree = self._postprocessTree(mmltree)
        return mmltree


    # protected:

    def _sanitizeEPS(self, data: str) -> str:
        data = data.replace('\r', '')
        data = data.replace('\n', '')
        data = data.replace('%' , '')
        return data


    def _extractMML(self, data: str) -> str:
        maths = re.findall(r"(<math.*</math>)", data)
        count = len(maths)
        if (count != 1):
            raise RuntimeError(f'passed file must contains only one <math> block but found {count} blocks')
        compressed   = maths[0]
        uncompressed = self._uncompressMML(compressed)
        return uncompressed

    def _uncompressMML(self, data: str) -> str:
        # Recover spaces betwean atributes
        # atr1="val1"atr2='val2' -> atr1="val1" atr2='val2'
        data = re.sub(r"([^=])'(\w)", r"\1' \2", data)
        data = re.sub(r'([^=])"(\w)', r'\1" \2', data)

        # Recover spaces betwean element names and theirs atributes
        # \note: < name ...> allows to 
        for token in self._tokens:
            data = data.replace('<' + token, '< ' + token + ' ')

        bChanged = True
        while bChanged:
            tempdata = data.replace('< ', '<').replace(' >', '>').replace('  ', ' ')
            bChanged = data != tempdata
            data     = tempdata

        return data.replace('<math>', '<math xmlns="http://www.w3.org/1998/Math/MathML">')


    def _generateTree(self, data: str) -> typing.Any:
        try:
            parser = etree.parse(mmltexPath)
            mmldom = etree.fromstring(data)
            mmldom = etree.XSLT(parser)(mmldom)
            return mmldom
        except:
            print(data)
            raise 


    def _postprocessTree(self, tree: etree) -> etree:
        return tree

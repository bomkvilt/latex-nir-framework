from .utiles.mathMLTokenFinder import MathMLTokenFinder
from .MMLFrontend import MMLFrontend
from .TeXBackend import TeXBackend
from argparse import ArgumentParser as AP
from glob import iglob as IG
from os import path
import os



class Type2TEX:
    def __init__(self,
        mmltex_path:str = ":/mmltex/mmltex.xsl",  # path to mmltex directory
        tokens_path:str = ":/utiles/tokens.json", # path to extracted mml tokens
        build_path:str  = "build/",               # path to a build directory root
        proj_path:str   = ".",                    # path to a project root directory
    ):
        self._module_root = path.dirname(path.realpath(__file__))
        self._mmltex_path = self._fixAbsPath(mmltex_path)
        self._tokens_path = self._fixAbsPath(tokens_path)
        self._build_path  = self._fixAbsPath(build_path )
        self._proj_path   = self._fixAbsPath(proj_path  )
        self._backend     = TeXBackend()
        self._frontend    = MMLFrontend(
            mmltex_path=mmltex_path, 
            tokens_path=tokens_path,
        )

    def assignToArgParser(self, parser:AP) -> any:
        parser.add_argument("path",
            help="path to a target entity")
        return self._doGeneration

    def generateEquations(self, scan_root:str, 
        bRecursive:bool = True,  # scan all subdirectories of a 'scan_root'
        bForceGen:bool  = False, # generate all equations including up-to-date ones
    ):
        for equation_path in IG(scan_root + '/**/*.eps', recursive=bRecursive):
            path0 = self._fixAbsPath(equation_path)
            path1 = self._generateEquation(path0, bForceGen)
            self._traceGeneration(path0, path1, path1 != "")
    
    def generateTokens(self):
        generator = MathMLTokenFinder(self._mmltex_path)
        generator.saveTokens(self._tokens_path)

# private: callbacks

    def _doGeneration(self, args):
        callback  = self.generateEquations        
        args.path = self._fixAbsPath(args.path)
        if args.path.count(":all:") == 0: 
            callback(args.path)
            return
        for subpath in IG(args.path.replace(":all:", "*"), recursive=False):
            callback(subpath)

# private: 

    def _generateEquation(self, equationPath:str, bForceGen:bool) -> str:
        texPath = self._deduceTeXFilePath(equationPath)
        if not self._isUpToDate(equationPath, texPath) or bForceGen:
            epsText = self._loadEquation(equationPath)
            texText = self._frontend.ParseEquation  (epsText)
            texText = self._backend .ProcessEquation(texText)
            self._saveEquation(texText, texPath)
            return texPath
        return ''

    def _isUpToDate(self, equationPath:str, texPath:str) -> bool:
        if not path.exists(texPath):
            return False
        
        if not path.exists(equationPath):
            raise RuntimeError('source .eps equation doesn`t exist : "{}"'.format(equationPath))
        
        if path.isdir(texPath):
            raise RuntimeError('destination file is a directory: "{}"'.format(texPath))
        
        # if .tex file is older than .eps one
        time0 = path.getmtime(equationPath)
        time1 = path.getmtime(texPath)
        return time1 >= time0
    
    def _deduceTeXFilePath(self, equationPath:str) -> str:
        equationPath = path.abspath(equationPath)
        outName = path.splitext(path.basename(equationPath))[0]
        outRoot = path.relpath (path.dirname (equationPath), self._proj_path)
        outPath = path.join(self._build_path, outRoot, outName + '.tex')
        return self._fixAbsPath(outPath)

    def _loadEquation(self, equationPath:str) -> str:
        return open(equationPath, 'r').read()

    def _saveEquation(self, texText:list, texPath:str):
        os.makedirs(os.path.dirname(texPath), exist_ok = True)
        with open(texPath, 'w', encoding="utf-8") as file:
            file.write(texText)
            file.close()

    def _traceGeneration(self, path0:str, path1:str, bDone:bool):
        path0 = (path.relpath(path0, self._proj_path).replace('\\', '/'))
        path1 = (path.relpath(path1, self._proj_path).replace('\\', '/') if bDone else path1)
        if bDone:   print("equation: '{}' -> '{}'".format(path0, path1))
        else:       print("equation: '{}' is up to date".format(path0))

# private: utiles

    def _fixAbsPath(self, inPath:str) -> str:
        if inPath.startswith(':/'):
            inPath = path.join(self._module_root, inPath[2:])
        inPath = path.abspath(inPath)
        return inPath.replace('\\', '/')

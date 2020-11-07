from .converter import XLSX2TeXConverter
from argparse import ArgumentParser as AP
from glob import iglob as IG
from os import path
import os



class XLSX2TeX:
    def __init__(self,
        build_path:str  = "build/", # path to a build directory root
        proj_path:str   = ".",      # path to a project root directory
    ):
        self._module_root = path.dirname(path.realpath(__file__))
        self._build_path  = self._fixAbsPath(build_path )
        self._proj_path   = self._fixAbsPath(proj_path  )
        self._converter   = XLSX2TeXConverter()

    def assignToArgParser(self, parser:AP) -> any:
        parser.add_argument("path",
            help="path to a target entity")
        return self._doGeneration

# private:

    def _doGeneration(self, args):
        callback  = self._generateTable        
        args.path = self._fixAbsPath(args.path)
        if args.path.count(":all:") == 0: 
            callback(args.path)
            return
        for subpath in IG(args.path.replace(":all:", "*"), recursive=False):
            callback(subpath)
    
    
    def _generateTable(self, scan_root:str):
        for sheet_path in IG(scan_root + '/**/*.xlsx', recursive=True):
            if sheet_path.count('~') > 0:
                continue
            path0 = self._fixAbsPath(sheet_path)
            path1 = self._generateEquation_(path0)
            self._traceGeneration(path0, path1, path1 != "")


    def _generateEquation_(self, sheet_path:str) -> str:
        table_path = self._deduceOutFilePath(sheet_path)
        if not self._isUpToDate(sheet_path, table_path):
            outText = self._converter.convert(sheet_path)
            self._saveOutput(outText, table_path)
            return table_path
        return ""

    def _deduceOutFilePath(self, sheet_path:str) -> str:
        sheet_path = path.abspath(sheet_path)
        outName = path.splitext(path.basename(sheet_path))[0]
        outRoot = path.relpath (path.dirname (sheet_path), self._proj_path)
        outPath = path.join(self._build_path, outRoot, outName + '.tex')
        return self._fixAbsPath(outPath)

    def _isUpToDate(self, sheet_path:str, table_path:str) -> bool:
        if not path.exists(table_path):
            return False        
        if not path.exists(sheet_path):
            raise RuntimeError('source .eps equation doesn`t exist : "{}"'.format(sheet_path))
        if path.isdir(table_path):
            raise RuntimeError('destination file is a directory: "{}"'.format(table_path))
        # if .tex file is older than .eps one
        time0 = path.getmtime(sheet_path)
        time1 = path.getmtime(table_path)
        return time1 >= time0

    def _loadInput(self, sheet_path:str) -> str:
        return open(sheet_path, 'r').read()
    
    def _traceGeneration(self, path0:str, path1:str, bDone:bool):
        path0 = (path.relpath(path0, self._proj_path).replace('\\', '/'))
        path1 = (path.relpath(path1, self._proj_path).replace('\\', '/') if bDone else path1)
        if bDone:   print("table: '{}' -> '{}'".format(path0, path1))
        else:       print("table: '{}' is up to date".format(path0))

    def _saveOutput(self, outText:list, table_path:str):
        os.makedirs(os.path.dirname(table_path), exist_ok = True)
        with open(table_path, 'w', encoding="utf-8") as file:
            file.write(outText)
            file.close()

    def _fixAbsPath(self, inPath:str) -> str:
        if inPath.startswith(':/'):
            inPath = path.join(self._module_root, inPath[2:])
        inPath = path.abspath(inPath)
        return inPath.replace('\\', '/')

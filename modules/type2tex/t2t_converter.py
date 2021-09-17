from ..includes import FTexworksConfig, JoinPath
from .t2t_converter_backend import T2TBackend
from .t2t_converter_frontend import T2TFrontend
from .settings import mmltexRoot, tokensPath

import os



class T2TConverter:
    def __init__(self, conf: FTexworksConfig) -> None:
        self._frontend = T2TFrontend()
        self._backend  = T2TBackend()
        self._conf     = conf

    def Convert(self, epspath: str, bForce: bool = False) -> None:
        # check if the equation is modified since last convertion
        texpath = self._deduceLaTeXEquationPath(epspath)
        if (self._isUpToDate(epspath, texpath, bForce)):
            return
        
        # generate LaTeX equation text from an on-disc file
        # \todo separate file reading and data processing
        mmltree = self._frontend.ProcessEPSFile(epspath)
        texText = self._backend.ProcessMMLTree(mmltree)

        # save a generated requation
        self._saveLaTeXEquation(texpath, texText)
        print(f'equation converted: {epspath} -> {texpath}')
    
    # protected:

    def _deduceLaTeXEquationPath(self, epspath: str) -> str:
        projroot  = self._conf.project_root
        docsdir   = self._conf.document_dir
        builddir  = self._conf.build_dir
        docsroot  = JoinPath([projroot, docsdir])
        buildroot = JoinPath([projroot, docsdir, builddir])
        
        relpath  = os.path.relpath(epspath, docsroot)
        filename = os.path.splitext(os.path.basename(relpath))[0] + '.tex'
        fileroot = os.path.dirname(relpath)
        return JoinPath([buildroot, fileroot, filename])

    def _saveLaTeXEquation(self, path: str, text: str) -> None:
        # create a base directory
        dirname = os.path.dirname(path)
        if os.path.exists(dirname): 
            if not os.path.isdir(dirname):
                raise RuntimeError(f'passed path is not a directory {path}')
        else:
            os.makedirs(dirname)
        # create a destination file
        with open(path, 'w') as file:
            file.write(text)

    def _isUpToDate(self, srcpath: str, destpath: str, bForce: bool) -> bool:
        # if source file not exists
        if (not os.path.exists(srcpath)):
            return True
        # if a destination file not exists
        if (not os.path.exists(destpath)):
            return False
        # check if paths are directories
        for path in [srcpath, destpath]:
            if (os.path.isdir(path)):
                raise RuntimeError(f'passed path is a directiry name {path}')
        # if force update is enabled
        if (bForce):
            return False
        # check update time
        time0 = os.path.getmtime(destpath)
        time1 = os.path.getmtime(srcpath)
        time2 = self._lastUpdateTime()
        return time0 >= time1 and time0 >= time2

    def _lastUpdateTime(self) -> float:
        t0 = self._backend.LastUpdateTime()
        return max([t0])

from __future__ import annotations
from ..includes import FTexworksConfig, JoinPath, FixPath

from glob import iglob
import os



class FAbstractInfo:
    def __init__(self) -> None:
        self.name  = '' # entity directory name
        self.path  = '' # entity directory path (absolute or script-relative)
        self.dpath = '' # entity directory path (document root relative)
        self.resources = dict[str, list[str]]()
        self.__default = False

    def MarkAsDefault(self, on: bool = True):
        self.__default = on

    def IsDefault(self) -> bool:
        return self.__default

    def GetResources(self, key: str) -> list[str]:
        if (key in self.resources):
            return self.resources[key]
        else:
            self.resources[key] = list[str]()
            return self.resources[key]

    def UpdateDPath(self, documentRoot: str) -> None:
        self.dpath = FixPath(os.path.relpath(self.path, documentRoot))


class FPartInfo(FAbstractInfo):
    def __init__(self) -> None:
        super().__init__()



class FSectionInfo(FAbstractInfo):
    def __init__(self) -> None:
        super().__init__()
        self.parts = dict[str, FPartInfo]()

    def GetPart(self, name: str) -> FPartInfo:
        if (name in self.parts):
            return self.parts[name]
        else:
            self.parts[name] = FPartInfo()
            return self.parts[name]

    def AddPart(self, part: FPartInfo) -> None:
        self.parts[part.name] = part

    def UpdateDPath(self, documentRoot: str) -> None:
        for partInfo in self.parts.values():
            partInfo.UpdateDPath(documentRoot)
        return super().UpdateDPath(documentRoot)



class FDocumentInfo(FAbstractInfo):
    def __init__(self) -> None:
        super().__init__()
        self.sectins = dict[str, FSectionInfo]()

    def GetSection(self, name: str) -> FSectionInfo:
        if (name in self.sectins):
            return self.sectins[name]
        else:
            self.sectins[name] = FSectionInfo()
            return self.sectins[name]

    def AddSection(self, section: FSectionInfo) -> None:
        self.sectins[section.name] = section

    def UpdateDPath(self, documentRoot: str) -> None:
        for sectionInfo in self.sectins.values():
            sectionInfo.UpdateDPath(documentRoot)
        super().UpdateDPath(documentRoot)



# \brief ProjectScanner class creates prject structure tree on
# base of abstract prject hierarchic structure
class ProjectScanner:
    
    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf   = conf
        self.typemap = dict[str, str](zip(
            conf.resourceTypes.values(), 
            conf.resourceTypes.keys()
        ))
    

    # ScanDocuments scans document root and section that matches passed section name
    def ScanDocuments(self, secname: str) -> FDocumentInfo:
        self._checkSectionName(secname)

        documentRoot = JoinPath([self._conf.project_root, self._conf.document_dir])
        documentInfo = FDocumentInfo()
        documentInfo.name = ''
        documentInfo.path = documentRoot

        sectionsRoot = JoinPath([documentRoot, self._conf.sections_dir])

        # scan for global resource folders
        self._scanResources(documentInfo, documentRoot)

        # scan sections
        for path in iglob(f'{sectionsRoot}/{secname}', recursive = False):
            if (not os.path.isdir(path)):
                continue
            path = FixPath(path)

            sectionInfo = self._scanSection(path)
            documentInfo.AddSection(sectionInfo)

        # setup entities
        documentInfo.UpdateDPath(documentRoot)

        return documentInfo


    # protected:

    def _scanSection(self, sectionRoot: str) -> FSectionInfo:
        secname = os.path.basename(sectionRoot)
        self._checkSectionName(secname)

        sectionInfo = FSectionInfo()
        sectionInfo.name = secname
        sectionInfo.path = sectionRoot

        partsRoot = JoinPath([sectionRoot, self._conf.parts_dir])

        # scan for section resource folders
        self._scanResources(sectionInfo, sectionRoot)

        # scan parts
        for path in iglob(f'{partsRoot}/*', recursive = False):
            if (not os.path.isdir(path)):
                continue
            path = FixPath(path)
            
            partInfo = self._scanSectionPart(path)
            sectionInfo.AddPart(partInfo)
        
        return sectionInfo


    def _scanSectionPart(self, partRoot: str) -> FPartInfo:
        partname = os.path.basename(partRoot)
        self._checkSectionPartName(partname)

        partInfo = FPartInfo()
        partInfo.name = partname
        partInfo.path = partRoot
        
        # scan for part resource folders
        self._scanResources(partInfo, partRoot)
        
        return partInfo


    def _scanResources(self, entityInfo: FAbstractInfo, entityRoot: str) -> None:
        for subpath in iglob(f'{entityRoot}/*', recursive = False):
            subpath = FixPath(subpath)
            dirname = os.path.basename(subpath)
            if (not dirname in self.typemap):
                continue
            type = self.typemap[dirname]

            entityInfo.GetResources(type).append(subpath)


    def _checkSectionName(self, name: str) -> None:
        forbiddenChars = ['/', '\\', ' ']
        for sequence in forbiddenChars:
            if (name.count(sequence) > 0):
                raise RuntimeError(f'passed name {name} contains invalid character "{sequence}"')
    

    def _checkSectionPartName(self, name: str) -> None:
        forbiddenChars = ['/', '\\']
        for sequence in forbiddenChars:
            if (name.count(sequence) > 0):
                raise RuntimeError(f'passed name {name} contains invalid character "{sequence}"')

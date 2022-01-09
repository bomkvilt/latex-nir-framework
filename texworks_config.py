from .common.path_works import PathWorks


class FTexworksConfig:
    def __init__(self) -> None:
        # basic project settings
        self.project_root = '.'

        # prject structure
        self.document_dir = 'documents'
        self.sections_dir = 'sections'
        self.parts_dir    = 'parts'
        self.build_dir    = 'build/TeX'
        self.pdf_dir      = 'build/pdf'

        # resource directories
        self.resourceTypes = {
            'figures'  : 'figs',
            'equations': 'eqns',
            'documents': 'docs',
        }

        # compilation settings
        self.latexCompiler = 'xelatex'
        self.latexArgs = [
            '-synctex=1',
            '-halt-on-error',
            '-interaction=nonstopmode',
        ]
        self.latexRenderArgs = [
            '-output-driver=xdvipdfmx -z1',
        ]
        self.latexAUXdir = '.'
        self.latexOutdir = '.'

    def GetResourceDir(self, type: str) -> str:
        if (type in self.resourceTypes):
            return self.resourceTypes[type]
        raise RuntimeError(f'passed resource type {type} is unknown')

    def GetDocumentRoot(self):
        return PathWorks.JoinPath(self.project_root, self.document_dir)

    def GetBuildRoot(self):
        return PathWorks.JoinPath(self.project_root, self.document_dir, self.build_dir)

    def GetPDFRoot(self):
        return PathWorks.JoinPath(self.project_root, self.document_dir, self.pdf_dir)
    
    def GetLatexOutroot(self):
        return PathWorks.JoinPath(self.project_root, self.document_dir, self.build_dir, self.latexOutdir)

    def GetLatexAUXdir(self):
        return PathWorks.JoinPath(self.build_dir, self.latexAUXdir)

    def GetLatexOutdir(self):
        return PathWorks.JoinPath(self.build_dir, self.latexOutdir)

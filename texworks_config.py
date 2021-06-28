
class FTexworksConfig:
    def __init__(self) -> None:
        # basic project settings
        self.project_root = '.'
        
        # prject structure
        self.document_dir = 'documents'
        self.sections_dir = 'sections'
        self.parts_dir    = 'parts'
        self.build_dir    = 'build/TeX'
        
        # resource directories
        self.resourceTypes = {
            'figures'  : 'figs',
            'equations': 'eqns',
            'documents': 'docs',
        }

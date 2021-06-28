from ...project_scanner import FSectionInfo

from jinja2 import Environment, FileSystemLoader

import os



class AutogenGenerator:

    def __init__(self) -> None:
        # generator source file directory
        self._root = os.path.dirname(os.path.realpath(__file__))

        # load template
        loader = FileSystemLoader(self._root)
        env    = Environment(loader = loader)
        self._template = env.get_template('autogen.templ.tex')


    def Generate(self, sectionInfo: FSectionInfo, outpath: str) -> None:
        outdata = self._template.render(vars = self._generateVars(sectionInfo))
        outdata = outdata.replace('<<', '{')
        outdata = outdata.replace('>>', '}')

        with open(outpath, 'w') as file:
            file.write(outdata)
            file.close()


    # protected:

    def _generateVars(self, sectionInfo: FSectionInfo) -> dict[str, str]:
        return [
            {
                'var': 'tmp1',
                'val': 'val1',
                'exp': 'long-long string',
            },
            {
                'var': 'tmp2',
                'val': 'val2',
                'exp': 'long-long string',
            }
        ]

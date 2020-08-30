import os.path as path
import lxml.etree as ET
import argparse
import glob
import json
import re
import os


class ToLaTeX:
    def __init__(self, build_path, proj_root, **kwargs):
        root = path.dirname(path.realpath(__file__))
        self.mmltex_path = path.join(root, "mmltex/mmltex.xsl")
        self.build_path  = build_path
        self.proj_root   = proj_root
        self.toks_path   = path.join(root, "utiles/tokens.json")
        # list of MathML tokens. Must have a contr-alphabical order
        self.toks_list   = json.load(open(self.toks_path, 'r'))
        self.toks_list   = sorted(self.toks_list)
        self.toks_list.reverse()
        # additoinal optoins
        self.bForce     = kwargs.get('bForce', False)
    
    # convert MathType .eps equaition into .tex equation
    #   \note: as a result the method will produce .tex
    #       files with non-wrapped equations
    #   \note: the converted doesn't convert up-to-date equations
    def convert(self, equation_path):
        tex_path = self.getTeXPath(equation_path)
        # is it need to generate a .tex file?
        if not self.checkTex(equation_path, tex_path) or self.bForce:
            mml_text = self.readMathML(equation_path)
            tex_text = self.genLaTeX(mml_text)
            tex_text = self.tuneTeXText(tex_text)
            self.saveLaTeX(tex_text, tex_path)
            return tex_path
        return 'up-to-date'

    # check if the TeX file is up to date
    def checkTex(self, equation_path, tex_path):
        if not path.exists(tex_path):
            return False
        if not path.exists(equation_path):
            raise RuntimeError('source .eps equation doesn`t exist : "{}"'.format(equation_path))
        if path.isdir(tex_path):
            raise RuntimeError('destination file is a directory: "{}"'.format(tex_path))
        
        # if .tex file is older than .eps one
        time0 = path.getmtime(equation_path)
        time1 = path.getmtime(tex_path)
        if (time0 > time1):
            return False
        return True

    # read MathML code from a MathType .eps file
    def readMathML(self, equation_path):
        file_path = equation_path
        file_data = open(file_path, 'r').read()
        file_data = file_data.replace("\r", "")
        file_data = file_data.replace("\n", "")
        file_data = file_data.replace("%" , "")
        mml_codes = re.findall(r"(<math.*</math>)", file_data)
        if len(mml_codes) != 1:
            raise RuntimeError('non-correct input file. Number of <math> blocks = {} != 1'.format(len(mml_codes)))
        return mml_codes[0]

    # convert MathML code into a non-wrapped LaTeX code
    def genLaTeX(self, mml_text):
        # as MathType code have no space it's need to recover them back
        # first we add them between element's atributes
        mml_text = re.sub(r"(\w)'(\w)", r"\1' \2", mml_text)

        # then we set them before the element's name and it's first atribute
        #   \note: as an element can be a subname of another one
        #       we sort them in descending order and add a leading ' '
        #       to mark the element as a visited
        for tok in self.toks_list:
            mml_text = mml_text.replace('<' + tok, '< ' + tok + ' ')

        # then we remove all unnidded spaces
        bContinue = True
        while bContinue:
            mml_text_new = mml_text.replace('< ', '<').replace(' >', '>').replace('  ', ' ')
            bContinue = mml_text_new != mml_text
            mml_text  = mml_text_new
        
        # then we generates the equation's DOM and convert it into a LaTeX
        mml_text = mml_text.replace('<math>', '<math xmlns="http://www.w3.org/1998/Math/MathML">')
        mml_dom  = ET.fromstring(mml_text)
        xslt     = ET.parse(self.mmltex_path)
        mml_dom  = ET.XSLT(xslt)(mml_dom)
        tex_text = str(mml_dom).replace('$', '')
        return tex_text

    # post-process a generated LaTeX equation
    def tuneTeXText(self, tex_text):
        tex_text = tex_text.replace(r'\frac', r'\dfrac')
        return tex_text
        
    # generate an outcomming .tex file's path
    def getTeXPath(self, equation_path):
        equation_path = path.abspath(equation_path)
        tex_name = path.splitext(path.basename(equation_path))[0]
        tex_path = path.relpath(path.dirname(equation_path), self.proj_root)
        tex_path = path.join(self.build_path, tex_path, tex_name + '.tex')
        tex_path = path.abspath(tex_path)
        return tex_path

    # save a latex code into a destination file
    def saveLaTeX(self, tex_text, tex_path):
        os.makedirs(path.dirname(tex_path), exist_ok=True)
        tex_file = open(tex_path, 'w')
        tex_file.write(tex_text)
        tex_file.close()


def buildEquations(proj_root, build_root, scan_root, **kwargs):
    converter = ToLaTeX(build_root, proj_root, **kwargs)
    for equation_path in glob.iglob(scan_root + '/**/*.eps', recursive=True):
        path0 = equation_path
        path1 = converter.convert(equation_path)
        print('equation: "{}" -> "{}"'.format(path0, path1).replace('\\', '/'))

# -------| main
parser = argparse.ArgumentParser()
parser.add_argument('scan_root',
    help='.eps root directory')
parser.add_argument('-p', '--proj_root', default=os.getcwd(),
    help='project root directory')
parser.add_argument('-b', '--build_root', default='build',
    help='directory to store resulting files')
parser.add_argument('-f', '--force', default=False, action='store_true',
    help='disable a lazy generation')
args = parser.parse_args()

buildEquations(args.proj_root, args.build_root, args.scan_root,
    bForce=args.force
)

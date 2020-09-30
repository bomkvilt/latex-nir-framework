from .utiles.mathMLTokenFinder import MathMLTokenFinder
from os import path
import re, os, glob, json, argparse
import lxml.etree as ET


class Type2TEX:
    def __init__(self, 
        mmltex_path:str = ":/mmltex/mmltex.xsl",  # path to mmltex directory
        tokens_path:str = ":/utiles/tokens.json", # path to extracted mml tokens
        build_path:str  = "build/",               # path to a build directory root
        proj_path:str   = ".",                    # path to a project root directory
    ):
        self.module_root = path.dirname(path.realpath(__file__))
        self.mmltex_path = self._fix_path_(mmltex_path)
        self.tokens_path = self._fix_path_(tokens_path)
        self.build_path  = self._fix_path_(build_path)
        self.proj_path   = self._fix_path_(proj_path)
        self.mml_tokens  = self._load_MMLtokens_()
    
    def assignToArgParser(self, parser:argparse.ArgumentParser) -> any:
        parser.add_argument("path",
            help="path to a target entity")
        return self._do_generation_

    def generateTokens(self):
        generator = MathMLTokenFinder(self.mmltex_path)
        generator.saveTokens(self.tokens_path)
    
    # convers MathType's .eps/none equation to a LaTeX's one
    #   \note: the method will produce a .tex file with a non-wrapped equation
    #       in a build directory (@self.build_path) in project root relative
    #       subdirectory.
    #   \note: by default if a destination file exists and it's modidficatin time
    #       is not older than a source file's one no generation will be done. But
    #       if a self.bForce flag is set the file file will be generated in any case.
    #   \ex:
    #           project root:   .
    #           build root:     ./build/
    #           scan_root:      ./equations/
    #           basic equation: ./equations/subdir/test.eps
    #           generated file: ./build/equations/subdir/test.tex
    def generateEquations(self, scan_root:str, 
        bRecursive:bool = True,  # scan all subdirectories of a 'scan_root'
        bForce_gen:bool = False, # generate all equations including up-to-date ones
    ):
        for equation_path in glob.iglob(scan_root + '/**/*.eps', recursive=bRecursive):
            path0 = self._fix_path_(equation_path)
            path1 = self._generate_equation_(path0, bForce_gen)
            self._print_convertion_status(path0, path1, path1 != "")

# private:
    def _do_generation_(self, args):
        callback  = self.generateEquations        
        args.path = self._fix_path_(args.path)
        count = args.path.count(":all:")
        if (count == 1 and not args.path.endswith(":all:")) or count > 1:
            raise RuntimeError(":all: placeholder must only be placed in the end of the path '{}'".format(args.path))
        if count == 0: 
            callback(args.path)
            return
        for subpath in glob.iglob(args.path.replace(":all:", "*"), recursive=False):
            callback(subpath)

    # replaces :/ token to the module's root path
    def _fix_path_(self, path0:str):
        if not path.isabs(path0) and path0.startswith(":/"):
            path0 = path.join(self.module_root, path0[2:])
        elif not path.isabs(path0):
            path0 = path.abspath(path0)
        return path0.replace("\\", "/")

    def _load_MMLtokens_(self):
        tokens = json.load(open(self.tokens_path, 'r'))
        tokens = sorted(tokens, reverse=True)
        return tokens

    def _generate_equation_(self, equation_path:str, bForce_gen:bool) -> str:
        tex_path = self._generate_tex_file_path(equation_path)
        if not self._is_up_to_date_(equation_path, tex_path) or bForce_gen:
            mml_text = self._readMathML_(equation_path)
            tex_text = self._genLaTeX_(mml_text)
            tex_text = self._tuneTeXText_(tex_text)
            self._saveLaTeX_(tex_text, tex_path)
            return tex_path
        return ""

    def _generate_tex_file_path(self, equation_path:str) -> str:
        equation_path = path.abspath(equation_path)
        tex_name = path.splitext(path.basename(equation_path))[0]
        tex_path = path.relpath(path.dirname(equation_path), self.proj_path)
        tex_path = path.join(self.build_path, tex_path, tex_name + '.tex')
        tex_path = path.abspath(tex_path)
        return self._fix_path_(tex_path)

    def _is_up_to_date_(self, equation_path:str, tex_path:str) -> bool:
        if not path.exists(tex_path):
            return False
        if not path.exists(equation_path):
            raise RuntimeError('source .eps equation doesn`t exist : "{}"'.format(equation_path))
        if path.isdir(tex_path):
            raise RuntimeError('destination file is a directory: "{}"'.format(tex_path))
        # if .tex file is older than .eps one
        time0 = path.getmtime(equation_path)
        time1 = path.getmtime(tex_path)
        return time1 >= time0

    # read MathML code from a MathType .eps file
    def _readMathML_(self, equation_path:str) -> str:
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
    def _genLaTeX_(self, mml_text:str) -> str:
        # as MathType's MathML code has no spaces we need to set them back first
        # Initialy, let's take them back between all attributes
        mml_text = re.sub(r"(\w)'(\w)", r"\1' \2", mml_text)

        # then we set them before the element's name and it's first atribute
        #   \note: as an element can be a subname of another one
        #       we sort them in descending order and add a leading ' '
        #       to mark the element as a visited
        for tok in self.mml_tokens:
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
    def _tuneTeXText_(self, tex_text:str) -> str:
        tex_text = tex_text.replace(r'\frac', r'\dfrac')
        return tex_text

    # save a latex code into a destination file
    def _saveLaTeX_(self, tex_text:str, tex_path:str):
        os.makedirs(path.dirname(tex_path), exist_ok=True)
        with open(tex_path, 'w') as tex_file:
            tex_file.write(tex_text)
            tex_file.close()

    def _print_convertion_status(self, path0:str, path1:str, bDone:bool):
        path0 = (path.relpath(path0, self.proj_path).replace("\\", "/"))
        path1 = (path.relpath(path1, self.proj_path).replace("\\", "/") if bDone else path1)
        if bDone:   print("equation: '{}' -> '{}'".format(path0, path1))
        else:       print("equation: '{}' is up to date".format(path0))

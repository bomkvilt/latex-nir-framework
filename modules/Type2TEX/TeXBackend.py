from ..common      import static_vars
from mako.template import Template
from functools     import reduce
from os import path
import re


### 
class TeXBackend:
    def __init__(self, 
        template_path:str = ':/templates/equations.templ.tex',
    ): 
        self._module_root  = path.dirname(path.realpath(__file__))
        self._templatePath = self._fixAbsPath(template_path)

    def ProcessEquation(self, rawTex:str) -> str:
        processor = _TeXProcessor(rawTex, self._templatePath)
        return processor.ProcessEquation()

# private: utiles

    def _fixAbsPath(self, inPath:str) -> str:
        if inPath.startswith(':/'):
            inPath = path.join(self._module_root, inPath[2:])
        inPath = path.abspath(inPath)
        return inPath.replace('\\', '/')


### places the strings into \text{} optional wrappers
def _textEscape(strings:list):
    strings = map(lambda c: r'(?:\\text{)?' + c + r'(?:})?', strings)
    return ''.join(strings)


### 
class _TeXProcessor:
    def __init__(self, rawTex:str,
        template_path:str
    ):
        self._texText = rawTex
        self._varExpls = []
        self._texLines = []
        self._equationData = []
        self._templatePath = template_path

    def ProcessEquation(self) -> str:
        # normalize input
        self._sanitizeEquatoin()
        # extract passed equation
        self._dropTextComments()
        self._extractExplanations()
        self._tuneEquation()
        self._splitEquations()
        # render template
        self._normalizeParsedData()
        return self._renderTeX()

# private:

    ### remove or replace unsupported symbols
    @static_vars( 
        dropRules = ['\u200b', '$' , '\r'],
        replRules = {
            '\\right\\ ': '\\right.',
        })
    def _sanitizeEquatoin(self, s={}):
        for char in s.dropRules:
            self._texText = self._texText.replace(char, '')
        for base, repl in s.replRules.items():
            self._texText = self._texText.replace(base, repl)

    ### remove in-equatin commentaries (starts with #)
    @static_vars( rule = re.compile( '(' r'\\text{#.*?}(?:\\text{.*?})*(?:\\\\)?' ')' ) )
    def _dropTextComments(self, stat={}):
        self._texText = stat.rule.sub('', self._texText)

    ###
    @static_vars(
        # regex that detects [; ...; ...] line
        shape = re.compile(''
            '('
                r'(?:\\left)?' +
                _textEscape([ r'\[', r'"', r'.*?', r'\]' ]) +
                r'(?:\\\\)?' +
            ')'
        ),
        # regex that detects line key and value
        parts = re.compile(''
            '\['          #
            '"' r'(.*?)'  # ; <key>
            '"' r'(.*)'   # ; <value>
            '\](?:\\\\)?' #
        ))
    def _extractExplanations(self, stat={}):
        # find all variable explanation blocks
        for m in stat.shape.finditer(self._texText):
            line = m.group(1)
            for tag in [r'\left', r'\right', r'\text{', '}']:
                line = line.replace(tag, '')
            
            m = stat.parts.match(line)
            if not m: raise RuntimeError('\n'
                'Incorrect variable explanation format: {}.\n'
                'The line must match pattern [" <variable>" <text>]'
                ''.format(line)
            )

            self._varExpls.append({
                'var' : str(m.group(1)),
                'expl': str(m.group(2)),
            })            
        # remove the blocks from the text
        self._texText = stat.shape.sub('', self._texText)

    @static_vars(
        body = re.compile(''
            r'^\s*'
            r'(\\begin{array}{.*?})?' # \1
            r'(.*?)'                  # \2
            r'(\\end{array})?'        # \3
            r'\s*$'
        ))
    def _splitEquations(self, stat={}):
        m = stat.body.match(self._texText)
        if not m: raise RuntimeError('\n'
            'Incorrect TeX equation body'
        )
        begin = m.group(1)
        body  = m.group(2)
        end   = m.group(3)

        lines = []
        if   (begin == '' and end == ''):
            lines = [body]
        elif (begin != '' and end != ''):
            lines = self._splitMulilineEquation(body)
        else: raise RuntimeError('\n'
            'Incorrect TeX equation body\n'
            'begin and end commands must be presented at the same time'
        )
        self._equationData = self._generateEquationData(lines)

    @static_vars( label = re.compile(r'\\left\[>>(.*?)\\right\]') )
    def _splitMulilineEquation(self, body:str, s={}) -> list:
        body  = s.label.sub(r'\\label{\1}', body)
        saldo = 0
        lines = []
        parts = body.split(r'\\')
        for part in parts:
            bNewLine = saldo == 0
            bgnCount = part.count(r'\begin{array}')
            endCount = part.count(r'\end{array}')
            saldo += bgnCount - endCount

            if (bNewLine): 
                lines.append(part)
            else:
                lines[-1] += r'\\' + part
        return lines
    
    @static_vars( label = re.compile(r'\\label{(.*?)}') )
    def _generateEquationData(self, lines:list, stat={}) -> str:
        data = []
        for line in lines:
            m = stat.label.search(line)
            data.append({
                'text' : line if not m else stat.label.sub('', line),
                'label': ''   if not m else m.group(1),
                'bTall': reduce(lambda a, b: a or b, [test in line for test in ['\\frac', '\\dfrac']]),
            })
        return data

    ### 
    @static_vars( rules = { r'\frac': r'\dfrac' } )
    def _tuneEquation(self, stat={}):
        for rule, repl in stat.rules.items():
            self._texText = self._texText.replace(rule, repl)

    @static_vars( empty = re.compile(r'^\s+$') )
    def _normalizeParsedData(self, s={}):
        self._equationData = list(filter(
            lambda eq: not s.empty.match(eq['text']), 
            self._equationData
        ))

    def _renderTeX(self) -> str:
        template = Template(filename=self._templatePath)
        return template.render(vars={
            'equations': self._equationData,
            'varexpls' : self._varExpls,
            'mode'     : self._getEquationMode(),
            'bTall'    : reduce(lambda a, b: a['bTall'] or b['bTall'], self._equationData),
        }).replace('\r', '').replace('\n\n', '\n')

    def _getEquationMode(self):
        bFlat = True
        for eq in self._equationData:
            bFlat &= eq['label'] == ''
        return 'flat' if bFlat else 'lines'

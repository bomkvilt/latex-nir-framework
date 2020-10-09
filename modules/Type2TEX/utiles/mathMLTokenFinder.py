import argparse, glob, json, re
import os.path as path


class MathMLTokenFinder:
    def __init__(self, scan_root):
        self.scan_root = scan_root
        self.xsl_toks  = self._findTokens_()

    def _findTokens_(self):
        xsl_toks_found = []
        for xsl_path in glob.iglob(path.join(self.scan_root + '*.xsl')):
            xsl_file = open(xsl_path, 'r')
            xsl_text = xsl_file.read()
            xsl_atrs = re.findall(r'<xsl:template match="([\w\:\|]+)">', xsl_text)
            
            for atr in xsl_atrs: 
                atrs = atr.split('|')
                atrs = filter(lambda a: a.startswith('m:'), atrs)
                xsl_toks_found += [cls.replace('m:', '') for cls in atrs]
        return sorted(list(set(xsl_toks_found)))

    def saveTokens(self, xsl_toks_path):
        with open(xsl_toks_path, 'w') as xsl_tok_file:
            json.dump(self.xsl_toks, xsl_tok_file, indent=4)
            xsl_tok_file.close()

# -------| main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('scan_root', help='mmltex directory')
    parser.add_argument('toks_json', help='json file with all found tokens')
    args = parser.parse_args()

    finder = MathMLTokenFinder(args.scan_root)
    finder.saveTokens(args.toks_json)

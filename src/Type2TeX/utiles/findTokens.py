import os.path as path
import argparse
import glob
import json
import re


def findTokens(scan_root):
    xsl_toks_found = []
    for xsl_path in glob.iglob(path.join(scan_root + '*.xsl')):
        xsl_file = open(xsl_path, 'r')
        xsl_text = xsl_file.read()
        xsl_toks = re.findall(r'<xsl:template match="m:(\w+)">', xsl_text)
        xsl_toks_found += xsl_toks
    return list(set(xsl_toks_found))

def saveTokens(xsl_toks_path, xsl_toks):
    xsl_tok_file = open(xsl_toks_path, 'w')
    json.dump(xsl_toks, xsl_tok_file)
    xsl_tok_file.close()

# -------| main
parser = argparse.ArgumentParser()
parser.add_argument('scan_root',
    help='mmltex directory')
parser.add_argument('toks_json',
    help='json file with all found tokens')
args = parser.parse_args()

toks = findTokens(args.scan_root)
saveTokens(args.toks_json, toks)


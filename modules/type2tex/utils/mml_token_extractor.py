from glob import iglob

import json
import os
import re


class MMLTokenExtractor:
    def __init__(self, mmltexRoot: str) -> None:
        self.mmltokens = self._extractTokens(mmltexRoot)

    def SaveTokensTo(self, outname: str) -> None:
        with open(outname, 'w') as file:
            json.dump(self.mmltokens, file, indent=4)
            file.close()


    # protected:

    def _extractTokens(self, mmltexRoot: str) -> list[str]:
        tokens = list[str]()

        for path in iglob(os.path.join(mmltexRoot, '*.xsl')):
            with open(path) as file:
                data = file.read()
                file.close()
            
            for match in re.findall(r'<xsl:template match="([\w\:\|]+)">', data):
                parts = match.split('|')
                parts = filter(lambda a: a.startswith('m:'), parts)
                tokens += [part.replace('m:', '') for part in parts]
        
        return sorted(list(set(tokens)))

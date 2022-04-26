import os
import re
import pickle
from pprint import pprint
from typing import Dict

all_codecs = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437',
'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857',
'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869',
'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125',
'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256',
'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr',
'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1',
'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7',
'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13',
'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u',
'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman',
'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213',
'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7',
'utf_8', 'utf_8_sig']

def smart_decoded(blob):
    result = ""
    for i in range( len(blob) - 1 ):
        b = blob[i:i+1]
        for codec in all_codecs:
            try:
                d = b.decode(codec)
                result += d
                break
            except:
                continue
    pattern = re.compile(r'\\x[0-9a-f][0-9a-f]')
    s = str(result.encode('utf-8'))[2:-1]
    result = str(re.sub(pattern, '', s))
    result = str(re.sub('\\\\[a-z]', ' ', result))
    return result

class SearchEngine:
    ''' Create a search engine object '''

    def __init__(self, indexing='index.pkl'):
        self.file_index = [] # directory listing returned by os.walk()
        self.indexing = indexing


    def create_new_index(self, values: Dict[str, str]) -> None:
        ''' Create a new file index of the root; then save to self.file_index and to pickle file '''
        root_path = values['PATH']
        self.file_index: list = [(root, files) for root, dirs, files in os.walk(root_path) if files]

        # save index to file
        with open(self.indexing,'wb') as f:
            pickle.dump(self.file_index, f)


    def load_existing_index(self) -> None:
        ''' Load an existing file index into the program '''
        try:
            with open(self.indexing,'rb') as f:
                self.file_index = pickle.load(f)
        except:
            self.file_index = []


    def search(self, values: Dict[str, str], smartdecode=True, write_output=False) -> None:
        ''' Search for the term based on the type in the index; the types of search
            include: contains, startswith, endswith; save the results to file '''
        results = []
        matches = 0
        records = 0
        term = values['TERM']

        # search for matches and count results
        for path, files in self.file_index:
            for file in files:
                records +=1
                if (values.get('CONTAINS', False) and term.lower() in file.lower() or
                    values.get('STARTSWITH', False) and file.lower().startswith(term.lower()) or
                    values.get('ENDSWITH', False) and file.lower().endswith(term.lower())):

                    result = os.path.join(path.replace('\\','/'), file).replace('\\','/')
                    results.append(result)
                    matches += 1
                else:
                    continue

        if write_output:
            # save results to file
            with open('search_results.txt','w') as f:
                for row in results:
                    f.write(row + '\n')

        return [ self.build_result(path, smartdecode=smartdecode) for path in results ], matches, records

    def build_result(self, path, N=2048, smartdecode=True):
        fileresult = {}

        head, tail = os.path.split(path)
        blob=None
        try:
            with open(path, 'rb') as f:
                blob = f.read(N)
        except Exception as ex:
            return {
                'file': tail,
                'location': head,
                'content': {
                    'blob': None,
                    'data': None
                }
            }
        try:
            return {
                'file': tail,
                'location': head,
                'content': {
                    'blob': smart_decoded(blob) if smartdecode else blob,
                    'data': self.content_aware(blob)
                },
            }

        except Exception as ex:
            return {
                'file': tail,
                'location': head,
                'content': {
                    'blob': smart_decoded(blob) if smartdecode else blob,
                    'data': None
                }
            }


    def content_aware(self, blob):
        try:
            import magic
        except ImportError as ex:
            return 'Python Magic library `python-magic` not found. Follow the instructions from here: https://github.com/ahupp/python-magic to install `python-magic` and libpython.'

        encoding = magic.from_buffer(blob)
        magicraw = magic.Magic(raw=True)
        raw = magicraw.from_buffer(blob)
        return { 'encoding': encoding, 'type': raw }
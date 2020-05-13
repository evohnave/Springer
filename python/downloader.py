# -*- coding: utf-8 -*-
"""
@author: Eric
"""

from pathlib import Path

import pandas as pd
import requests as r

# Constants
# Url comes from article announcing release... will download an Excel workbook
BOOKS = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v5/'

PWD = Path('J:/Springer')

FILE_TYPES = {
        'pdf': 'content/pdf',
        'epub': 'download/epub'
    }

def fix_author(author):
    ''' prepare author name '''
    authr = list(map(str.strip, author.split(' ')))
    ret = {}
    ret['last'] = authr[-1].strip(' ')
    if len(authr) == 1:
        ret['full'] = ret['last']
    else:
        ret['full'] = ', '.join([ret['last'], ' '.join(authr[:-1]).strip(' ')])
    return ret

def springer_downloader():
    ''' Downloads all pdfs and epubs from Springer Nature '''
    springer = pd.read_excel(BOOKS)
    # We care about:
    #  - Book Title
    #  - Author(s)
    #  - OpenURL <- used for download

    for _, row in springer.iterrows():
        # get and clean book title
        book_title = row['Book Title'].replace(':', '-')        # colons not allowed
        book_title = book_title.replace('/', '-')               # slashed neither
        book_title = book_title.strip()
        # get author(s)
        authors = list(map(str.strip, row['Author'].split(', ')))
        # get isbn
        url = row['OpenURL']
        for file_type in FILE_TYPES:
            # download once, save as many times as necessary by author
            dl_url = r.get(url).url
            dl_url = dl_url.replace('book', FILE_TYPES[file_type])
            file = r.get(dl_url)
            if file.status_code == 200:
                # file successfully downloaded; if not, prob an epub that isn't
                for author in authors:
                    authr = fix_author(author)
                    folder = authr['full']
                    name = ''.join([authr['last'], ' - ', book_title, '.', file_type])
                    file_path = PWD.joinpath('/'.join([folder, name]))
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'wb') as wrt:
                        wrt.write(file.content)

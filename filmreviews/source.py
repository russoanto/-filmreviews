from typing import Protocol
from whoosh import fields
from whoosh.fields import Schema
from whoosh.index import Index, FileIndex


class Source(Protocol):
    
    ''' name of the source '''
    name : str

    ''' Schema of IR '''
    shcema : Schema




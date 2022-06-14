import tomatoes, index_gen,movie_search
import json
import os
from concurrent import futures
import time
from whoosh import fields
from whoosh import index
from whoosh.fields import Schema
from whoosh.index import Index, FileIndex
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from tqdm import tqdm
import signal
import time
import readchar



MAX_WORKERS = 4

def main():
    ix = index_gen.index_film()

    searcher = movie_search.movie_search()
    data = searcher.readIndex()




    pomodoro = tomatoes.indexTomatoes(data)

    pomodoro.scrape_all_information()
    pomodoro.indexing()
    



    search = pomodoro.ix.searcher()
    #print(list(searcher.lexicon("content")))
    type_search = input('Inserire Il campo su cui ricercare: ')
    parser = QueryParser(type_search, schema=pomodoro.ix.schema)
    title = input('Inserire il parametro: ')
    query = parser.parse(type_search+":"+title)
    results = search.search(query)
    if len(results) == 0:
        print("Empty result!!")
    else:
        for x in results:
            print(x)

main()

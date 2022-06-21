from operator import imod
import tomatoes,movie_search,imdbClass
import json
import os
from concurrent import futures
import time
import re
import math
from whoosh import fields
from whoosh import index
from whoosh.fields import Schema
from whoosh.index import Index, FileIndex
from whoosh.qparser import syntax, Plugin, QueryParser, MultifieldPlugin
from whoosh.analysis import RegexTokenizer,StemFilter

from whoosh.index import open_dir
from tqdm import tqdm

import merge_search



class FieldBoosterPlugin(Plugin):
        #boosts: Dict[str, float]

        def __init__(self, boosts):
            self.boosts = boosts

        def filters(self, parser):
            # Run just before MultifieldPlugin (110)
            return [(self.do_boost, 105)]

        def do_boost(self, parser, group):
            for i, node in enumerate(group):
                if isinstance(node, syntax.GroupNode):
                    # Recurse inside groups
                    group[i] = self.do_boost(parser, node)
                elif node.has_fieldname and node.fieldname is not None:
                    node.set_boost(node.boost * self.boosts.get(node.fieldname, 1.0))
            return group

def compute_discounted_cumulative_gain(data):
    if len(data) == 0:
        return 0
    return data[0] + sum([(data[i] / math.log(i + 1, 2)) for i in range(1, len(data))])

def getInformation_indexing(get):
    '''
    Fa scraping e indexing delle due fonti, imdb e pomodoro (get riceve uno dei due alla volta).
    '''
    print("entro, ", type(get))
    get.get_all_information_t()
    get.indexing()

def printInformation(result):
    '''
    stampa le informazioni della singola classe imdb o pomodoro
    '''
    if result.has_matched_terms():
        scores = []
        for x in result:
            print(x["title"] + ' --> ' + str(x.score)+ '\n')
            scores.append(x.score)

def searchInIndex(queryPom, queryImd, searchPOM, searchIMD):
    # #--------------------------------------------------------

    # im = QueryParser(None, imdb.ix.schema, group=syntax.OrGroup)
    # fieldboosts = {
    #         'title': 6,
    #         'content':1,
    # }
    # mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    # im.add_plugin(mfp)


    # p.add_plugin(FieldBoosterPlugin({
    #         'title':40,'content':40,'release_date':40,'genres':40,'directors':40,'casts':40,
    # }))
    print(queryImd, " ", queryPom)
    searchers = [(searchPOM,'tomato'), (searchIMD,'imdb')]
    top_k = merge_search.aggregate_search(queryPom, searchers, 5)

    with open('./informations.txt', 'w') as openfile:
        for i in top_k:
            for j in i:
                openfile.write(str(j)+ ' ')
            openfile.write('\n')

    resultsIMD = searchIMD.search(queryImd,terms=True, limit=20)
    resultsPOM = searchPOM.search(queryPom, terms=True, limit=20)

    printInformation(resultsIMD)
    printInformation(resultsPOM)

def main():

    searcher = movie_search.movie_search()
    data = searcher.readIndex()

    pomodoro = tomatoes.indexTomatoes(data)

    imdb = imdbClass.imdbIndex("./movies/index.json", data, "https://www.imdb.com")

    # getInformation_indexing(imdb)
    # getInformation_indexing(pomodoro)
    
    searchPOM = pomodoro.ix.searcher()
    searchIMD = imdb.ix.searcher()

    p = QueryParser(None, pomodoro.ix.schema, group=syntax.OrGroup)
    fieldboosts = {
            'title': 6,
            'content':1,
    }
    mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    p.add_plugin(mfp)


    p.add_plugin(FieldBoosterPlugin({
            'title':40, 'casts':40, 'release_date':40,'genres':40,'directors':40,'content':40,
    }))
    
    inQuery = input('Inserire il parametro: ')
    query_txt = re.sub("\s+[1I]$", "", inQuery.strip())

    #elaboro query
    queryPom = p.parse(query_txt)
    queryImd = p.parse(inQuery)
    
    searchInIndex(queryPom, queryImd, searchPOM, searchIMD) #ricerca negli index richiama anche la funzione printInformation()


main()

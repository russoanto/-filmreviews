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
import readchar



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


def main():

    searcher = movie_search.movie_search()
    data = searcher.readIndex()

    pomodoro = tomatoes.indexTomatoes(data)

    imdb = imdbClass.imdbIndex("./movies/index.json", data, "https://www.imdb.com")
    # imdb.get_all_information_t()
    # imdb.indexing()
    # pomodoro.scrape_all_information()
    # pomodoro.indexing()
    
    #search = pomodoro.ix.searcher()
    search = imdb.ix.searcher()


    p = QueryParser(None, pomodoro.ix.schema, group=syntax.OrGroup)
    fieldboosts = {
            'title': 6,
            'content':1,
    }
    mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    p.add_plugin(mfp)


    p.add_plugin(FieldBoosterPlugin({
            'title':40, 'casts':40, 'release_date':40,'genres':40,'directors':40,
    }))
    title = input('Inserire il parametro: ')
    query_txt = re.sub(r"\s+[1I]$", "", title.strip())

    query = p.parse(query_txt)
    results = search.search(query,terms=True,limit=None)
    # Was this results object created with terms=True?
    if results.has_matched_terms():
        scores = []
        for x in results:
            print(x["title"]+' '+str(x.score))
            scores.append(x.score)
        print(compute_discounted_cumulative_gain(scores))
    


main()


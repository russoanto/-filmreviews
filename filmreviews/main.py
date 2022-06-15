import tomatoes,movie_search
import json
import os
from concurrent import futures
import time
from whoosh import fields
from whoosh import index
from whoosh.fields import Schema
from whoosh.index import Index, FileIndex
from whoosh.qparser import syntax, Plugin, QueryParser, MultifieldPlugin
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


def main():

    searcher = movie_search.movie_search()
    data = searcher.readIndex()

    pomodoro = tomatoes.indexTomatoes(data)

    # pomodoro.scrape_all_information()
    # pomodoro.indexing()
    

    search = pomodoro.ix.searcher()
    #print(list(searcher.lexicon("content")))
    #type_search = input('Inserire Il campo su cui ricercare: ')
    p = QueryParser(None, pomodoro.ix.schema, group=syntax.OrGroup)
    fieldboosts = {
            'title': 6,
            'content':1,
    }
    mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    p.add_plugin(mfp)
        # adds custom set boosts to each field in case the user specifically selects one of them with "field:value"
        # some fields are already boosted by default like "name" but an additional boost can be added by specifing it
    p.add_plugin(FieldBoosterPlugin({
            'name':40, 'casts':40, 'release_date':40,'genres':40,'directors':40,
    }))
    title = input('Inserire il parametro: ')
    query = p.parse(title)
    results = search.search(query,terms=True,limit=None)
    # Was this results object created with terms=True?
    if results.has_matched_terms():
        for x in results:
            print(x["title"])
    


main()

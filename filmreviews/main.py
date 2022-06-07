import tomatoes, index_gen,movie_search
import json
import os
import asyncio

def main():
    ix = index_gen.index_film()
    #num = ix.create_index()
    #ix.save_index()
    #line = index_gen.index_film().resume_index()
    # if line != None:
    #     elem = line.split(' ')
    #     ix = index_gen.index_film(elem[0],elem[1],elem[2],elem[3],elem[4])
    searcher = movie_search.movie_search()
    data = searcher.readIndex()
    test = tomatoes.tomatoes('./index/index.json')
    test.get_movies_info(data,1)
    # with open(test.path_index) as json_file:
    #     data = json.load(json_file)
    #     test.get_movies_info(data,1)
        #test.movie_reviews(test.format_name('Spider Man'))
main()

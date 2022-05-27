import tomatoes, index_gen
import json
import os
import asyncio

def main():
    ix = index_gen.index_film()
    num = ix.create_index()
    test = tomatoes.tomatoes(ix.get_path(),num)

    with open(test.path_index) as json_file:
        data = json.load(json_file)
        print(test.get_movies_info(data,2))
    #print(test.movie_reviews('spiderman'))
    
main()

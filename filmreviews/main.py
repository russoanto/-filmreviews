import tomatoes, index_gen
import json
import os
import asyncio

def main():
    #ix = index_gen.index_film()
    #num = ix.create_index()
    #ix.save_index()
    line = index_gen.index_film().resume_index()
    if line != None:
        elem = line.split(' ')
        ix = index_gen.index_film(elem[0],elem[1],elem[2],elem[3],elem[4])
        test = tomatoes.tomatoes(ix.get_path(),ix.get_num_film())
        with open(test.path_index) as json_file:
            data = json.load(json_file)
            test.get_movies_info(data,1)
        #test.movie_reviews(test.format_name('Spider Man'))
main()

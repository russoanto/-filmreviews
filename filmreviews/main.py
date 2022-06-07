import tomatoes, index_gen,movie_search
import json
import os
from concurrent import futures
import time
from whoosh import fields
from whoosh.index import create_in
from whoosh.fields import Schema
from whoosh.index import Index, FileIndex

MAX_WORKERS = 4

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
    #test = tomatoes.tomatoes('./index/index.json')
    #test.get_movies_info(data,1)
    # with open(test.path_index) as json_file:
    #     data = json.load(json_file)
    #     test.get_movies_info(data,1)
        #test.movie_reviews(test.format_name('Spider Man'))



    pomodoro = tomatoes.indexTomatoes('./index/index.json')
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    ix = create_in("indexdir", pomodoro.schema)
    
    titles = []
    for i in data["movies"]:
        titles.append(pomodoro.format_name(i["title"]))


    def download_all(film_name):
        desc = pomodoro.movie_desc(film_name)
        casts = pomodoro.movie_casts(film_name)
        reviews = pomodoro.movie_reviews(film_name)
        direct = pomodoro.movie_info(film_name)
        print(desc + '\n' + str(casts) + '\n' + str(reviews) + '\n' + str(direct))

    def download_many(data):

    #    for title in sorted(titles):
    #         download_all(title)
    
        with futures.ThreadPoolExecutor(2) as executor:
            to_do = []
            for title in sorted(titles):
                future = executor.submit(download_all,title)
                to_do.append(future)

            result = []
            for future in futures.as_completed(to_do):
                res = future.result()

    # for i in range(len(data["movies"])):
    #     film_name = pomodoro.format_name(data["movies"][i]["title"])
    #     id = data["movies"][i]["id"]

    #     time.sleep(2)
    download_many(data)

main()

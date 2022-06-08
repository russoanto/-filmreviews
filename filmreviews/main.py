import tomatoes, index_gen,movie_search
import json
import os
from concurrent import futures
import time
from whoosh import fields
from whoosh.index import create_in
from whoosh.fields import Schema
from whoosh.index import Index, FileIndex
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from tqdm import tqdm



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
    else:
        ix = open_dir("indexdir")
    
    titles = []
    for i in data["movies"]:
        titles.append(pomodoro.format_name(i["title"]))


    # def download_all_info(film_name):
    #     rsp = []
    #     rsp.append(pomodoro.movie_info(film_name)) #regista e altre info
    #     if("not_exists" in rsp[0]):
    #         return []
    #     rsp.append(pomodoro.movie_desc(film_name)) #descrizione
    #     rsp.append(pomodoro.movie_casts(film_name)) #casts
    #     rsp.append(pomodoro.movie_reviews(film_name)) #reviews
    #     return rsp

    def download_all_info(film_name,date):
        resp = pomodoro.get_movie_info(pomodoro.format_name(film_name),str(date))
        return resp

    def write_all_info(data,i,writer):
        if i % 200 == 0:
            time.sleep(10)
        resp = download_all_info(pomodoro.format_name(data["movies"][i]["title"]),data["movies"][i]["release_date"])
        if(resp != []):
            writer.add_document(id=str(data["movies"][i]["id"]),title=data["movies"][i]["title"],content=resp[0])
        

    def download_many(data):
    #    for title in sorted(titles):
    #         download_all(title)

        with futures.ThreadPoolExecutor(50) as executor:
            to_do = []
            with ix.writer() as writer:
                for i in tqdm(range(len(data["movies"]))):
                    future = executor.submit(write_all_info,data,i,writer)
                    to_do.append(future)

                    result = []
                    for future in futures.as_completed(to_do):
                        res = future.result()

    def download_many_iter(data):
        for i in range(20):
            with ix.writer() as writer:
                write_all_info(data, i, writer)

    # for i in range(len(data["movies"])):
    #     film_name = pomodoro.format_name(data["movies"][i]["title"])
    #     id = data["movies"][i]["id"]

    #     time.sleep(2)
    #download_many(data)
    #download_all_info('Spider-Man')

    searcher = ix.searcher()
    #print(list(searcher.lexicon("content")))
    parser = QueryParser("content", schema=ix.schema)
    query = parser.parse(u"content:Guy")
    results = searcher.search(query)
    if len(results) == 0:
        print("Empty result!!")
    else:
        for x in results:
            print(x)

main()

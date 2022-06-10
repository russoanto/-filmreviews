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
import signal
import time
import readchar



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
            if(i % 100 == 0):
                time.sleep(5)
            resp = download_all_info(pomodoro.format_name(data["movies"][i]["title"]),data["movies"][i]["release_date"])
            if(resp != []):
                writer.add_document(id=str(data["movies"][i]["id"]),title=data["movies"][i]["title"],content=resp[0],directors=resp[1][0])
        
    

    def download_many(data,start,end):
    #    for title in sorted(titles):
    #         download_all(title)
        with ix.writer() as writer: 
            with futures.ThreadPoolExecutor(10) as executor:
                to_do = []
                for i in tqdm(range(start,end)):
                    future = executor.submit(write_all_info,data,i,writer)
                    to_do.append(future)

                    result = []
                    for future in futures.as_completed(to_do):
                        res = future.result()



    def iter_download_many(data):

        flag = input('Resume?')
        if(flag == 'y' or flag == 'Y'):
            save_path = "./index/resume.txt"

            if os.path.exists(save_path):
                resume_file = open(save_path,'r')
                line = resume_file.readline()
            lines = line.split('-')
            lines = list(map(int,lines))
            resume_point = lines[0] + 1
            print(lines)
            print(resume_point)
            chunk = lines[1]
            start = lines[2] + 1
            if(resume_point == 29):
                end = range(len(data["movies"])) - start
            else:
                end = start + chunk
        else: 
            resume_point = 0
            chunk = int(len(data["movies"])/30)
            start = 0
            end = start + chunk

        for i in range(resume_point,30):
            download_many(data, start,end)
            start = end + 1
            if(i == 29):
                end = range(len(data["movies"])) - start
            else:
                end = start + chunk
            save_result(str(i)+'-'+str(chunk)+'-'+str(end))
            time.sleep(10)

    
    def save_result(response):
            with open('./index/resume.txt', "w") as openfile:
                openfile.write(response)


    # for i in range(len(data["movies"])):
    #     film_name = pomodoro.format_name(data["movies"][i]["title"])
    #     id = data["movies"][i]["id"]

    #     time.sleep(2)

    #iter_download_many(data)

    # with ix.writer() as writer: 
    #     resp = download_all_info(pomodoro.format_name('Top Gun'),'1998')
    #     if(resp != []):
    #         writer.add_document(id='12345',title='Top Gun',content=resp[0])
    
    # with ix.writer() as writer: 
    #     resp = download_all_info(pomodoro.format_name('Spider Man'),'2001')
    #     if(resp != []):
    #         writer.add_document(id='4534534',title='Spider Man',content=resp[0])
    

    search = ix.searcher()
    #print(list(searcher.lexicon("content")))
    type_search = input('Inserire Il campo su cui ricercare: ')
    parser = QueryParser(type_search, schema=ix.schema)
    title = input('Inserire il parametro: ')
    query = parser.parse(type_search+":"+title)
    results = search.search(query)
    if len(results) == 0:
        print("Empty result!!")
    else:
        for x in results:
            print(x)

main()

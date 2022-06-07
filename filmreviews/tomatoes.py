import requests
import json
from bs4 import BeautifulSoup
import index_gen,movie_search
from concurrent import futures
import threading
import time
from whoosh import fields
from whoosh.fields import Schema
from whoosh.index import Index, FileIndex
import os, os.path


class tomatoes:

    def __init__(self,path_index,url = "https://www.rottentomatoes.com/m/"):
        self.path_index = path_index
        self.url = url


    def movie_desc(self, name):
        desc = ""
        req = requests.get(self.url+str(name))
        if req.status_code != 404:
            soup = BeautifulSoup(req.content, 'html.parser') 
            for i in soup.find_all('div', class_="movie_synopsis clamp clamp-6 js-clamp"):
                desc += i.get_text() 
            return desc
        return "not_exists : " + name
    
    def movie_info(self,name):
        resp = []
        req = requests.get(self.url+str(name))
        if req.status_code != 404:
            soup = BeautifulSoup(req.content, 'html.parser') 
            for i in soup.find_all('li', class_="meta-row clearfix"):
                if "Director" in i.get_text() or "Streaming" in i.get_text():
                    tmp = str(i.get_text()).replace('\n','')
                    tmp = tmp.replace('\t', '')
                    tmp = tmp.replace('\r','')
                    tmp = tmp.replace('\n', '')
                    resp.append(tmp)
            return resp
        return "not_exists : " + name

    def movie_casts(self,name):
        resp = []
        req = requests.get(self.url+str(name))
        if req.status_code != 404:
            soup = BeautifulSoup(req.content, 'html.parser') 
            count = 0
            for i in soup.find_all('a', class_="unstyled articleLink"):
                if(count == 3):
                    tmp = str(i.get_text()).replace('\n','')
                    tmp = tmp.replace('\t', '')
                    tmp = tmp.replace('\r','')
                    tmp = tmp.replace('\n', '')
                    resp.append(tmp.strip())
                if 'View All' in i.get_text():
                    count += 1
            return resp
        return "not_exists : " + name       
    
    def movie_reviews(self, name):
        
        reviews = []
        req = requests.get(self.url+name+"/reviews/")
        print(name + ": "+ self.url+str(name)+"/reviews/")
        if req.status_code != 404:
            soup = BeautifulSoup(req.content, 'html.parser')
            for i in soup.find_all('div', class_="review_desc"):
                review = str(i.get_text()).replace('\n','')
                review = review.replace('\t','')
                review = review.replace('\r', '')
                review = review.replace('Full Review', '')
                review = review.replace('|', '')
                reviews.append(review.strip())
        else:
            print("not_exists")
        if reviews != []:
            with open('./index/reviews.txt','a') as openfile:
                openfile.write(name + ": " + str(reviews)+"\n")
        else:
            print('\t\t'+name + ": "+ self.url+str(name)+"/reviews/")

        return reviews
    #
    # ritorna la descrizione di tutti i film raccolti dall'indice creato
    #
    def get_movies_info(self,data, type_mode=0):
        with futures.ThreadPoolExecutor(max_workers=4) as executor:
            to_do = []
            count = 0
            for i in range(len(data["movies"])):
                    film_name = tomatoes.format_name(data["movies"][i]["title"])
                    # if count == 10:
                    #     time.sleep(0.5)
                    #     print("SLEEP")
                    #     count = 0

                    if type_mode == 0:
                        future = executor.submit(self.movie_info,film_name)
                    else:
                        future= executor.submit(self.movie_reviews,film_name)
                    to_do.append(future)
                   
                    msg = 'Scheduled for {}: {}'
                    print(msg.format(film_name, future))
                    count += 1

            results = []
            for future in futures.as_completed(to_do):
                res = future.result()
                print(msg.format(future,res))                
                results.append(res.strip())
            return results

    @staticmethod
    def format_name(name):
        film_name = name.lower()
        film_name = film_name.replace(' ','_')
        film_name = film_name.replace('\'','')
        film_name = film_name.replace('-', '_')
        film_name = film_name.replace(',','')
        return str(film_name)

    def test_iter(self,data):
        for i in range(int(self.num_film)):
            film_name = tomatoes.format_name(data[str(i)]["name"])
            self.movie_reviews(film_name)
    def prova(self,data):
        for i in range(len(data["movies"])):
            film_name = tomatoes.format_name(data["movies"][i]["title"])
            print(film_name)
            print(self.movie_reviews(film_name))

class indexTomatoes(tomatoes):
    def __init__(self,schema,path_index,url = "https://www.rottentomatoes.com/m/"):
        self.schema = Schema(
            id = fields.ID(unique=True,stored=True),
            title=fields.TEXT(stored=True),  
            content=fields.TEXT(stored=True), 
            release_date=fields.DATETIME(stored=True),
            reviews = fields.TEXT(stored=True),
            genres = fields.KEYWORD(stored=True),
            directors = fields.KEYWORD(stored=True),
            casts = fields.KEYWORD(stored=True),
            runtime = fields.TEXT(stored=True),
        )
        self.path_index = path_index
        self.url = urlchema(tit)

# test = tomatoes('./index/index.json')
# print(test.movie_casts(test.format_name('Spider man')))
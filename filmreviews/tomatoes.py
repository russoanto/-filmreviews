import requests
import json
from bs4 import BeautifulSoup
import index_gen,movie_search
import concurrent.futures
import threading
import time
from whoosh import fields
from whoosh import index
from whoosh.fields import Schema
from tqdm import tqdm
import re
import os, os.path

class tomatoes:

    def __init__(self,path_index,url = "https://www.rottentomatoes.com/m/"):
        self.path_index = path_index
        self.url = url


    def movie_desc(self, param):
        desc = ""
        name = param[0]
        date = param[1]
        soup = param[2]

        #soup = BeautifulSoup(req.content, 'html.parser') 
        for i in soup.find_all('div', class_="movie_synopsis clamp clamp-6 js-clamp"):
            tmp = str(i.get_text()).replace('\n','')
            tmp = re.sub(' +', ' ', tmp)
            desc += tmp.strip()
        return desc
    
    @staticmethod
    def format_output(stringa):
        stringa = stringa.split(':')
        stringa = stringa[1].split(',')
        return stringa[0]
    
    #TODO da cambiare il return
    def movie_info(self,param):
        resp = []
        name = param[0]
        date = param[1]
        soup = param[2] #era req
        #soup = BeautifulSoup(req.content, 'html.parser') 
        for i in soup.find_all('li', class_="meta-row clearfix"):
            tmp = str(i.get_text()).replace('\n','')
            tmp = re.sub(' +', ' ', tmp)
            resp.append(tmp.strip())
            for i in resp:
                if 'Director' in i:
                    return tomatoes.format_output(i)
        return ''
        

    def movie_casts(self,param):
        resp = []
        name = param[0]
        date = param[1]
        soup = param[2]
        #soup = BeautifulSoup(req.content, 'html.parser') 
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
        return resp[:-1]

    
    def movie_reviews(self, param):
        reviews = []
        name = param[0]
        date = param[1]
        req = requests.get(self.url+name+"/reviews/")
        if req.status_code != 404:
            soup = BeautifulSoup(req.content, 'html.parser')
            for i in soup.find_all('div', class_="review_desc"):
                review = str(i.get_text()).replace('\n','')
                review = review.replace('\t','')
                review = review.replace('\r', '')
                review = review.replace('Full Review', '')
                review = review.replace('|', '')
                review = re.sub(' +', ' ', review)
                reviews.append(review.strip())
        else:
            req = requests.get(self.url+name+'_'+date+"/reviews/")
            if req.status_code != 404:
                soup = BeautifulSoup(req.content, 'html.parser')
                for i in soup.find_all('div', class_="review_desc"):
                    review = str(i.get_text()).replace('\n','')
                    review = review.replace('\t','')
                    review = review.replace('\r', '')
                    review = review.replace('Full Review', '')
                    review = review.replace('|', '')
                    review = re.sub(' +', ' ', review)
                    reviews.append(review.strip())
            else:          
                print("not_exists: " + name)
        return reviews



    #
    # ritorna la descrizione di tutti i film raccolti dall'indice creato
    #
    def get_movie_info(self,film_name,date):
        req = requests.get(self.url+str(film_name))
        ret = [] # vuota nel caso in cui il film non sia stato trovato
        params = [film_name,date]
        if req.status_code != 404:
            params.append(req)
            with futures.ThreadPoolExecutor(4) as executor:

                future_desc =executor.submit(tomatoes.movie_desc,self,params)
                future_info = executor.submit(tomatoes.movie_info,self,params)
                future_rev = executor.submit(tomatoes.movie_reviews,self,params)
                future_casts = executor.submit(tomatoes.movie_casts,self,params)

                desc = future_desc.result()
                info = future_info.result()
                rev = future_rev.result()
                cast = future_casts.result()
                if desc != '':
                    ret.append(desc)
                    ret.append(info)
                    ret.append(rev)
                    ret.append(cast)
                print(ret)
        else:
            req = requests.get(self.url+film_name+'_'+date)
            if req.status_code != 404:
                params.append(req)
                with futures.ThreadPoolExecutor(4) as executor:

                    future_desc =executor.submit(tomatoes.movie_desc,self,params)
                    future_info = executor.submit(tomatoes.movie_info,self,params)
                    future_rev = executor.submit(tomatoes.movie_reviews,self,params)
                    future_casts = executor.submit(tomatoes.movie_casts,self,params)

                    desc = future_desc.result()
                    info = future_info.result()
                    rev = future_rev.result()
                    cast = future_casts.result()
                    if desc != '':
                        ret.append(desc)
                        ret.append(info)
                        ret.append(rev)
                        ret.append(cast)
                    print(ret)
        
        return ret
               
                
    #TODO Aggiungere filto per troppi trattini, attraverso le regex massimo un trattino 
        
    @staticmethod
    def format_name(name):
        film_name = name.lower()
        film_name = film_name.replace(' ','_')
        film_name = film_name.replace('\'','')
        film_name = film_name.replace('-', '_')
        film_name = film_name.replace(',','')
        film_name = film_name.replace(':','')
        return str(film_name)

    def test_iter(self,data):
        for i in range(int(self.num_film)):
            film_name = tomatoes.format_name(data[str(i)]["name"])
            self.movie_reviews(film_name)


#TODO Spostaare i metodi per la costruzione dell'indice in questa classe (quelli presenti nel main)
class indexTomatoes(tomatoes):
    def __init__(self,path_index,data,url = "https://www.rottentomatoes.com/m/"):
        if not os.path.exists("indexdir"):
            os.mkdir("indexdir")
            self.schema = Schema(
                id = fields.ID(unique=True,stored=True),
                title=fields.TEXT(stored=True),  
                content=fields.TEXT(stored=True), 
                #release_date=fields.DATETIME(stored=True),
                #reviews = fields.TEXT(stored=True),
                #genres = fields.KEYWORD(stored=True),
                directors = fields.TEXT(stored=True),
                casts = fields.TEXT(stored=True),
                #runtime = fields.TEXT(stored=True),
            )
            self.ix = index.create_in("indexdir", self.schema)
        else:
            self.ix = index.open_dir("indexdir")

        self.path_index = path_index
        self.url = url
        self._MOVIES = []
        self.films = []
        for i in range(len(data["movies"])):
            self.films.append({'id':data["movies"][i]["id"],'title':data["movies"][i]["title"],'date':data["movies"][i]["release_date"]})

    def scrape_all_information(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(self.get_all_information, self.films)

    def get_all_information(self,film):
        name = self.format_name(film["title"])
        id_film = film["id"]
        param = [name,film["date"]]
        richiesta = requests.get(self.url+name)
        if richiesta.status_code != 404:
            soup = BeautifulSoup(richiesta.content, 'html.parser')
            param.append(soup)
            desc = self.movie_desc(param)
            if desc != "":
                info = self.movie_info(param)
                casts = self.movie_casts(param)
                rev = self.movie_reviews(param)
                film_schema = {'id':id,'title':name,'id':id_film,'overview':desc,'directors':info,'casts':casts,'reviews':rev}
                self._MOVIES.append(film_schema)
                print(film_schema)

        else:
            richiesta = requests.get(self.url+name+'_'+date)
            if richiesta.status_code != 404:
                soup = BeautifulSoup(richiesta.content, 'html.parser')
                param.append(soup)
                desc = self.movie_desc(param)
                if desc != "":
                    info = self.movie_info(param)
                    casts = self.movie_casts(param)
                    rev = self.movie_reviews(param)
                    film_schema = {'id':id,'title':name,'id':id_film,'overview':desc,'directors':info,'casts':casts,'reviews':rev}
                    self._MOVIES.append(film_schema)
                    print(film_schema)

    def indexing(self):
        self.writer = self.ix.writer()
        for i in tqdm(range(len(self._MOVIES))):
            self.writer.add_document(
                id=str(self._MOVIES[i]["id"]),
                title=self._MOVIES[i]["title"],
                content=self._MOVIES[i]["overview"],
                directors = self._MOVIES[i]["directors"],
                casts=list(set(self._MOVIES[i]["casts"])),
            )
        self.writer.commit()



    



# test = tomatoes('./index/index.json')
# print(test.movie_info([test.format_name('Spider-man'),'2001']))
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
        req = requests.get(self.url+str(name))
        if req.status_code != 404:
            soup = BeautifulSoup(req.content, 'html.parser') 
            for i in soup.find_all('div', class_="movie_synopsis clamp clamp-6 js-clamp"):
                tmp = str(i.get_text()).replace('\n','')
                tmp = re.sub(' +', ' ', tmp)
                desc += tmp.strip()
            return desc
        else:
            req = requests.get(self.url+str(name)+'_'+date)
            if req.status_code != 404:
                soup = BeautifulSoup(req.content, 'html.parser') 
                for i in soup.find_all('div', class_="movie_synopsis clamp clamp-6 js-clamp"):
                    tmp = str(i.get_text()).replace('\n','')
                    tmp = re.sub(' +', ' ', tmp)
                    desc += tmp.strip()
                return desc
        return "not_exists : " + name
    
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
        req = requests.get(self.url+str(name))
        if req.status_code != 404:
            soup = BeautifulSoup(req.content, 'html.parser') 
            for i in soup.find_all('li', class_="meta-row clearfix"):
                    tmp = str(i.get_text()).replace('\n','')
                    tmp = re.sub(' +', ' ', tmp)
                    resp.append(tmp.strip())
            try:
                direc = tomatoes.format_output(resp[3])
                runtime = tomatoes.format_output(str(resp[9]))
            except IndexError:
                return ['',''] 
            return [direc,runtime]
        else:
            req = requests.get(self.url+str(name)+'_'+date)
            if req.status_code != 404:
                soup = BeautifulSoup(req.content, 'html.parser') 
                for i in soup.find_all('li', class_="meta-row clearfix"):
                    
                        tmp = str(i.get_text()).replace('\n','')
                        tmp = re.sub(' +', ' ', tmp)
                        resp.append(tmp.strip())
                try:
                    direc = tomatoes.format_output(resp[3])
                    runtime = tomatoes.format_output(str(resp[9]))
                except IndexError:
                    return ['',''] 
                return [direc,runtime]
        return "not_exists : " + name

    def movie_casts(self,param):
        resp = []
        name = param[0]
        date = param[1]
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
        else:
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
        if reviews != []:
            #with open('./index/reviews.txt','a') as openfile:
                #openfile.write(name + ": " + str(reviews)+"\n")
                pass
        else:
            #print('\t\t'+name + ": "+ self.url+str(name)+"/reviews/")
            pass

        return reviews

    #
    # ritorna la descrizione di tutti i film raccolti dall'indice creato
    #

    def get_movie_info(self,film_name,date):
        params = [film_name,date]
        with futures.ThreadPoolExecutor(4) as executor:

            future_desc =executor.submit(tomatoes.movie_desc,self,params)
            future_info = executor.submit(tomatoes.movie_info,self,params)
            future_rev = executor.submit(tomatoes.movie_reviews,self,params)
            future_casts = executor.submit(tomatoes.movie_casts,self,params)

            ret = []
            ret.append(future_desc.result())
            ret.append(future_info.result())
            ret.append(future_rev.result())
            ret.append(future_casts.result())
            if ret == []:
                print("BHO")
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
    def prova(self,data):
        for i in range(len(data["movies"])):
            film_name = tomatoes.format_name(data["movies"][i]["title"])
            print(film_name)
            print(self.movie_reviews(film_name))

class indexTomatoes(tomatoes):
    def __init__(self,path_index,url = "https://www.rottentomatoes.com/m/"):
        self.schema = Schema(
            id = fields.ID(unique=True,stored=True),
            title=fields.TEXT(stored=True),  
            content=fields.TEXT(stored=True), 
            #release_date=fields.DATETIME(stored=True),
            #reviews = fields.TEXT(stored=True),
            #genres = fields.KEYWORD(stored=True),
            directors = fields.KEYWORD(stored=True),
            #casts = fields.KEYWORD(stored=True),
            #runtime = fields.TEXT(stored=True),
        )
        self.path_index = path_index
        self.url = url

    



# test = tomatoes('./index/index.json')
# print(test.movie_info([test.format_name('Spider-man'),'2001']))
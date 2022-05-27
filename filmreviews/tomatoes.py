import requests
import json
from bs4 import BeautifulSoup
import index_gen
from concurrent import futures
import threading


class tomatoes:

    def __init__(self,path_index,num_film,url = "https://www.rottentomatoes.com/m/"):
        self.path_index = path_index
        self.num_film = num_film
        self.url = url

    def movie_info(self, name:str) -> str:
        desc = ""
        if requests.get(self.url+str(name)).status_code != 404:
            soup = BeautifulSoup(requests.get(self.url+str(name)).content, 'html.parser') 
            for i in soup.find_all('div', class_="movie_synopsis clamp clamp-6 js-clamp"):
                desc += i.get_text() 
            return desc
        return "not_exists : " + name
    
    def movie_reviews(self, name:str) -> str:
        reviews = []
        soup = BeautifulSoup(requests.get(self.url+str(name)+"/"+"reviews").content, 'html.parser') 
        for i in soup.find_all('div', class_="review_desc"):
            review = str(i.get_text()).replace('\n','')
            review = review.replace('\t','')
            review = review.replace('\r', '')
            review = review.replace('Full Review', '')
            review = review.replace('|', '')
            reviews.append(review)
        return reviews


    #
    # ritorna la descrizione di tutti i film raccolti dall'indice creato
    #
    def get_movies_info(self,data):
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for i in range(self.num_film):
                    film_name = data[str(i)]["name"]
                    film_name = film_name.lower()
                    film_name = film_name.replace(' ','_')


                    future = executor.submit(self.movie_info,data[str(i)]["name"])
                    to_do.append(future)
                    msg = 'Scheduled for {}: {}'
                    print(msg.format(film_name, future))

            results = []
            for future in futures.as_completed(to_do):
                res = future.result()
                #print(msg.format(future,res))
                if(not res.find('not_exists')):
                    results.append(res)
            return results
    def test_iter(self,data):
        for i in range(self.num_film):
            film_name = data[str(i)]["name"]
            film_name = film_name.lower()
            film_name = film_name.replace(' ','_')
            print(self.movie_info(film_name))


#test = tomatoes()
# with open(test.path_index) as json_file:
#     data = json.load(json_file)
#     for i in range(test.num_film):
#          print(test.movie_info(data[str(i)]["name"]))

# for i in test.movie_reviews(input("Inserire nome film: ")):
#     print(i)
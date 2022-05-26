import requests
import json
from bs4 import BeautifulSoup
import index_gen
from concurrent import futures


class tomatoes:
    url = "https://www.rottentomatoes.com/m/"
    indice_film = index_gen.index_film()
    path_index = indice_film.get_path()
    num_film = indice_film.create_index()

    def movie_info(self, name:str) -> str:
        desc = ""
        soup = BeautifulSoup(requests.get(self.url+str(name)).content, 'html.parser') 
        for i in soup.find_all('div', class_="movie_synopsis clamp clamp-6 js-clamp"):
            desc += i.get_text() 
        return desc
    
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
        with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
                print(msg.format(future,res))
                results.append(res)
            return results

test = tomatoes()
# with open(test.path_index) as json_file:
#     data = json.load(json_file)
#     for i in range(test.num_film):
#          print(test.movie_info(data[str(i)]["name"]))

with open(test.path_index) as json_file:
    data = json.load(json_file)
    print(test.get_movies_info(data))

# for i in test.movie_reviews(input("Inserire nome film: ")):
#     print(i)
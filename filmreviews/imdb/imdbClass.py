import os
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from concurrent import futures
import requests
import movie_search

class imdb:

    def __init__(self, path_index, data, url):
        self.url = url
        self.path_index = path_index
        self._MOVIES = []
        self.films = []
        for i in range(len(data["movies"])):
            self.films.append({'id':data["movies"][i]["id"],'title':data["movies"][i]["title"],'date':data["movies"][i]["release_date"]})
        
    @staticmethod
    def format_name(name):
        film_name = name.lower()
       # film_name = film_name.replace(' ','+')
        film_name = film_name.replace('\'','')
        film_name = film_name.replace('-', '_')
       # film_name = film_name.replace(',','')
       # film_name = film_name.replace(':','')
        return str(film_name)

    def get_movie_info(self, film_name, date):
        return [film_name, date]

    def scrapingDownload(self, name, url):
        self.url += '/find?q=' #inserisco il link corretto.
        headers = {"Accept-Language": "en-US,en;q=0.5"}
        name = 'sonic the hedgehog 2'

        self.url += name + '&title_type=feature&sort=year,asc'
            #'&title_type=feature&release_date=1986-01-01,&sort=year,asc&view=advanced'
        print(self.url)
        soup = BeautifulSoup(requests.get(self.url, headers=headers).content, 'html.parser') 
        for i in soup.find_all('a'):
           # print(i.get_text().lower().lstrip().rstrip(), " ", str(name).lower())
            if(i.get_text().lower().strip()== str(name)):
                print(i.get('href'))
                break
        try:
            self.url = 'https://www.imdb.com' + i.get('href') + 'reviews?sort=userRating&dir=desc&ratingFilter=0'
            soup = BeautifulSoup(requests.get(self.url, headers=headers).content, 'html.parser') 
            count=0
            print(self.url)
            for i in soup.find_all('div', class_='text show-more__control'):
                print(i.get_text(),'\n')
                count +=1
            print(count)
        except:
            print("è successo")
        self.resetUrl(url)

    def resetUrl(self, url):
        self.url = url


searcher = movie_search.movie_search()
data = searcher.readIndex()
test = imdb("/movies/index.json", data,  "https://www.imdb.com")
resp = []
for i in range(len(data["movies"])):
    resp.append(test.get_movie_info(test.format_name(data["movies"][i]["title"]),data["movies"][i]["release_date"]))
for i in range(len(data["movies"])):
    print(resp[i])
for i in range(len(data["movies"])):
    test.scrapingDownload(resp[i][0], "https://www.imdb.com")

#test.file_json()

'''
for i in range(0, 9440):
    test.scrapingDowload(fileJson[i]["title"])
''' 
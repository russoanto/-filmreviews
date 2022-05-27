import os
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from concurrent import futures
import json
import requests
import urllib3

 
'''
class imdb:
    def __init__():
'''


def scrapingDowload(name, year = ''):
    newname = name
    url = 'https://www.imdb.com/find?q='
    url += name + '&title_type=feature&sort=year,asc'
        #'&title_type=feature&release_date=1986-01-01,&sort=year,asc&view=advanced'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser') 
    for i in soup.find_all('a' ):
        #print(i.get_text())
        if(i.get_text().lower() == str(name).lower()):
            print(i.get('href'))
            break
    try:
        url = 'https://www.imdb.com' + i.get('href') + 'reviews?sort=userRating&dir=desc&ratingFilter=0'
        soup = BeautifulSoup(requests.get(url).content, 'html.parser') 
        count=0
        print(url)
        for i in soup.find_all('div', class_='text show-more__control'):
            print(i.get_text(),'\n')
            count +=1
        print(count)
    except:
        print("è successo")

# with open(test.path_index) as json_file:
#     data = json.load(json_file)
#     for i in range(test.num_film):
#          print(test.movie_info(data[str(i)]["name"]))
with open("../index/final_index.json") as json_file:
    data = json.load(json_file)
    for i in range(0, 43899):
        scrapingDowload(data[str(i)]["name"])
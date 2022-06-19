import os
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from concurrent import futures
import requests
import movie_search

import concurrent.futures
import time

from whoosh import fields
from whoosh import index
from whoosh.fields import Schema
from tqdm import tqdm
from analyzer import StandardAnalyzer_num


class imdb:

    def __init__(self, path_index, data, url):
        self.url = url
        self.path_index = path_index

        #print(self.films)
        
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

    def get_reviews(self,soup):
        count=0
        reviews = []
        #print(self.url)
        for i in soup.find_all('div', class_='text show-more__control'):
            #print(i.get_text(),'\n')
            reviews.append(i.get_text())
            count +=1
        return reviews
            #print(count)





    #########################

    def get_rating(self, soup):
        rating = ''
        for span in soup.find_all('span', class_='sc-7ab21ed2-1 jGRxWM'):
            #print(span.text)   
            rating += span.text
            break
        return rating

    def get_content(self,soup):
        content = ''
        for div in soup.find_all('span', class_='sc-16ede01-1 kgphFu'):
            content += div.text
        return content


    def get_genres(self, soup):
        genres = []
        for div in soup.find_all('div', class_='ipc-chip-list sc-16ede01-4 bMBIRz'):
            for a in div.contents:
                #print(a.text) 
                genres.append(a.text)
            break
        return ','.join(genres)
    
    #sarebbe l'elemento 2 ma a volte manca il "pegi"
    def get_duration(self, soup):
        durata = ''
        for ul in soup.find_all('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-8c396aa2-0 kqWovI baseAlt'):
            #print(ul.contents[2].text)
            if(len(ul.contents)==3):
                #print(ul.contents[2].text)
                durata += ul.contents[2].text
            elif(len(ul.contents)==2):
                #print(ul.contents[1].text)
                durata += ul.contents[1].text
            break
        return durata

    
    #ho fatto cosi perchè hanno tutti la stessa classe, sono dovuto scendere ai vari livelli partendo dalla classe di partenza
    def get_director_writers_starts(self, soup):
        writers = []
        actors_l = []
        director = []

        for ul in soup.find_all('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt'):
            #print(i.get_text(),'\n')
            lilist = ul.contents
            
            #director
            director.append(lilist[0].contents[1].text)
            #print(lilist[0].contents[1].text)
            
            #writers
            for actors in lilist[1].contents[1].contents[0]:
                #print(act.prettify())
                writers.append(actors.contents[0].contents[0].text)
                #print(actors.contents[0].contents[0].text)
                
            #stars
            for stars in lilist[2].contents[1].contents[0]:
                #print(stars.prettify())
                actors_l.append(stars.contents[0].contents[0].text)
                #print(stars.contents[0].contents[0].text)
            
            break
        return (','.join(writers),','.join(actors_l),','.join(director))


    
# f = open("demofile3.txt", "a")


# searcher = movie_search.movie_search()
# data = searcher.readIndex()
# test = imdb("/movies/index.json", data,  "https://www.imdb.com")
# resp = []
# # for i in tqdm(range(len(data["movies"]))):
# #     resp.append(test.get_movie_info(test.format_name(data["movies"][i]["title"]),data["movies"][i]["release_date"]))
# #     print(resp[i])
# #     test.scrapingDownload(resp[i][0])
    
# test.get_all_information_t()

# f.close()


#test.file_json()

'''
for i in range(0, 9440):
    test.scrapingDowload(fileJson[i]["title"])
''' 

class imdbIndex(imdb):
    def __init__(self, path_index, data, url):
        self.url = url
        self.path_index = path_index
        self.films = []
        for i in range(len(data["movies"])):
            self.films.append({'id':data["movies"][i]["id"],'title':imdb.format_name(data["movies"][i]["title"]),'date':data["movies"][i]["release_date"]})
        self._MOVIES = []
        if not os.path.exists("indexdirIMDB"):
            os.mkdir("indexdirIMDB")
            self.schema = Schema(
                id = fields.ID(unique=True,stored=True),
                title=fields.TEXT(stored=True,analyzer=StandardAnalyzer_num(),sortable=True),  
                content=fields.TEXT(stored=True), 
                release_date=fields.TEXT(stored=True),
                reviews = fields.STORED,
                genres = fields.TEXT(stored=True),
                directors = fields.TEXT(stored=True),
                casts = fields.TEXT(stored=True),
                runtime = fields.TEXT(stored=True),
                rating = fields.NUMERIC(stored=True),
            )
            self.ix = index.create_in("indexdirIMDB", self.schema)
        else:
            self.ix = index.open_dir("indexdirIMDB")

    def scrapingDownload(self,film):
        self.url += '/find?q=' #inserisco il link corretto.
        headers = {"Accept-Language": "en-US,en;q=0.5"}

        self.url += film["title"] + '&title_type=feature&sort=year,asc'
            #'&title_type=feature&release_date=1986-01-01,&sort=year,asc&view=advanced'
        #print(self.url)

        start = time.time()
        richiesta = requests.get(self.url, headers=headers)
        end = time.time()

        if richiesta.status_code != 404:
            soup = BeautifulSoup(richiesta.content, 'html.parser')
            for i in soup.find_all('a'):
            # print(i.get_text().lower().lstrip().rstrip(), " ", str(name).lower())
                if(i.get_text().lower().strip()== str(film["title"])):
                    #print(i.get('href'))
                    self.url = 'https://www.imdb.com' + i.get('href') + '?ref_=tt_urv'
                    break
       #print(self.url)
            start = time.time()
            richiesta = requests.get(self.url, headers=headers)
            end = time.time()
            if end-start >= 6:
                time.sleep(10)
            elif end-start >= 2:
                time.sleep(5)
        #print(richiesta.status_code)
            if richiesta.status_code != 404:
                soup = BeautifulSoup(richiesta.content, 'html.parser') 
        
                ###################################
                #qua chiamo tutte le funzioni
                try:
                    test = self.get_director_writers_starts(soup)
                    # for j in test[0]:
                    #     print(j)
                    # for j in test[1]:
                    #     print(j)
                    # for j in test[2]:
                    #     print(j)
                    durata = self.get_duration(soup)
                    genres = self.get_genres(soup)
                    rating = self.get_rating(soup)
                    content = self.get_content(soup)
                    #print(durata + " " + genres + " " + rating + " \n" + content + "\n")
                except:
                    f.write(str(self.url))
                    f.write('\n')
                ################################
                reviews = []
                try:
                    self.url = 'https://www.imdb.com' + i.get('href') + 'reviews?sort=userRating&dir=desc&ratingFilter=0'
                    soup = BeautifulSoup(requests.get(self.url, headers=headers).content, 'html.parser') 
                    reviews.append(self.get_reviews(soup))
                except:
                    reviews = []
                self.resetUrl("https://www.imdb.com")

                if content != '':
                    film_schema = {
                    'id':film["id"],
                    'title':film["title"],
                    'release':film["date"],
                    'content':content,
                    'reviews':reviews,
                    'directors':test[2],
                    'writers':test[0],
                    'actors':test[1],
                    'genres':genres,
                    'rating':float(rating),
                    'runtime':durata,
                    }
                    print(film_schema)
                    self._MOVIES.append(film_schema)
        print("------------------------------")
        

    def resetUrl(self, url):
        self.url = url
    
    def get_all_information_t(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(self.scrapingDownload,self.films)
    
    def indexing(self):
        self.writer = self.ix.writer()
        ids = set()
        for i in tqdm(range(len(self._MOVIES))):
            if self._MOVIES[i]["id"] not in ids:
                self.writer.add_document(
                    id=str(self._MOVIES[i]["id"]),
                    title=self._MOVIES[i]["title"],
                    content=self._MOVIES[i]["content"],
                    release_date = self._MOVIES[i]["release"],
                    reviews=self._MOVIES[i]["reviews"],
                    genres=self._MOVIES[i]["genres"],
                    directors = self._MOVIES[i]["directors"],
                    casts=self._MOVIES[i]["actors"],
                    runtime = self._MOVIES[i]["runtime"],
                    rating = self._MOVIES[i]["rating"],
                )
                ids.add(self._MOVIES[i]["id"])
        self.writer.commit()

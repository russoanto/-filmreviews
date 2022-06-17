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

        self.url += name + '&title_type=feature&sort=year,asc'
            #'&title_type=feature&release_date=1986-01-01,&sort=year,asc&view=advanced'
        #print(self.url)


        soup = BeautifulSoup(requests.get(self.url, headers=headers).content, 'html.parser') 

        

        for i in soup.find_all('a'):
           # print(i.get_text().lower().lstrip().rstrip(), " ", str(name).lower())
            if(i.get_text().lower().strip()== str(name)):
                #print(i.get('href'))
                self.url = 'https://www.imdb.com' + i.get('href') + '?ref_=tt_urv'
                break
        print("------------------------------")
        print(self.url)

        soup = BeautifulSoup(requests.get(self.url, headers=headers).content, 'html.parser') 

        ###################################
        #qua chiamo tutte le funzioni
        try:
            self.get_director_writers_starts(soup)
            self.get_duration(soup)
            self.get_genres(soup)
            self.get_rating(soup)
        except:
            f.write(str(self.url))
            f.write('\n')


        ################################

        try:
            self.url = 'https://www.imdb.com' + i.get('href') + 'reviews?sort=userRating&dir=desc&ratingFilter=0'
            soup = BeautifulSoup(requests.get(self.url, headers=headers).content, 'html.parser') 
            count=0
            print(self.url)
            for i in soup.find_all('div', class_='text show-more__control'):
                #print(i.get_text(),'\n')
                count +=1
            #print(count)
        except:
            print("è successo")
        self.resetUrl(url)

    def resetUrl(self, url):
        self.url = url


    #########################

    def get_rating(self, soup):
        
        for span in soup.find_all('span', class_='sc-7ab21ed2-1 jGRxWM'):
            print(span.text)   
            break


    def get_genres(self, soup):
        for div in soup.find_all('div', class_='ipc-chip-list sc-16ede01-4 bMBIRz'):
            for a in div.contents:
                print(a.text)    
            break
    
    #sarebbe l'elemento 2 ma a volte manca il "pegi"
    def get_duration(self, soup):
        for ul in soup.find_all('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-8c396aa2-0 kqWovI baseAlt'):
            #print(ul.contents[2].text)
            if(len(ul.contents)==3):
                print(ul.contents[2].text)
            elif(len(ul.contents)==2):
                print(ul.contents[1].text)
            break

    
    #ho fatto cosi perchè hanno tutti la stessa classe, sono dovuto scendere ai vari livelli partendo dalla classe di partenza
    def get_director_writers_starts(self, soup):
        for ul in soup.find_all('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt'):
            #print(i.get_text(),'\n')
            lilist = ul.contents
            
            #director
            print(lilist[0].contents[1].text)
            
            #writers
            for actors in lilist[1].contents[1].contents[0]:
                #print(act.prettify())
                print(actors.contents[0].contents[0].text)
                
            #stars
            for stars in lilist[2].contents[1].contents[0]:
                #print(stars.prettify())
                print(stars.contents[0].contents[0].text)
                
            
            break
            
f = open("demofile3.txt", "a")


searcher = movie_search.movie_search()
data = searcher.readIndex()
test = imdb("/movies/index.json", data,  "https://www.imdb.com")
resp = []
for i in range(len(data["movies"])):
    resp.append(test.get_movie_info(test.format_name(data["movies"][i]["title"]),data["movies"][i]["release_date"]))
    #print(resp[i])
    test.scrapingDownload(resp[i][0], "https://www.imdb.com")

f.close()

#test.file_json()

'''
for i in range(0, 9440):
    test.scrapingDowload(fileJson[i]["title"])
''' 
import requests
import json
import time

url = "https://advanced-movie-search.p.rapidapi.com/genre/movie/list"

 #Qui ho vari headers per le richieste get delle API vito che quelle gratuite sono limitate a 500 al mese

# headers = {
# 	"X-RapidAPI-Host": "advanced-movie-search.p.rapidapi.com",
# 	"X-RapidAPI-Key": "2f578134c9msha2d0e92b52a1562p114a96jsn29f99d2ca53b"
# }

# headers_2 = {
#     'X-RapidAPI-Host': 'advanced-movie-search.p.rapidapi.com',
#     'X-RapidAPI-Key': '4581bee7e0msh00a097b3e544861p17d736jsna6aeef75fb56'
# }

# headers = {
# 	"X-RapidAPI-Host": "advanced-movie-search.p.rapidapi.com",
# 	"X-RapidAPI-Key": "5a0d0d71a7msh325031a0ddf7fc8p1ee1e2jsn0efd03be1707"
# }

headers = {
	"X-RapidAPI-Host": "advanced-movie-search.p.rapidapi.com",
	"X-RapidAPI-Key": "59124b1fbdmsh7cb07020705c585p11f13ejsn635ddd484fd0"
}


class movie_search:
    base_url = 'https://advanced-movie-search.p.rapidapi.com/'
    url_genre = 'https://advanced-movie-search.p.rapidapi.com/genre/movie/list'
    url_search = 'https://advanced-movie-search.p.rapidapi.com/discover/movie'
    path_index = './index/index.json'


    def getGenre(self):
        self.genr = requests.request("GET", self.url_genre, headers=headers).text
        return self.genr


    # Attraverso le API ottengo un json con 20 film
    def getSinglePageMovie(self,querystring):

        r = requests.get(self.url_search, headers=headers, params=querystring)
        print(r.status_code)
        if(r.status_code == 500):
            return {'message':'exit'}
        elif (r == {'message': 'You have exceeded the rate limit per second for your plan, BASIC, by the API provider'} or r.status_code==429):
            return {'message':'wait'}
        
        return r.json()

    #attraverso una richiesta alle API crea una lista con i codici dei vari generi che dovranno essere usate per la ricerca dei film
    def getGenrId(self): 
        genre = json.loads(self.getGenre())
        self.genreId = []
        for i in range(len(genre["genres"])):
            self.genreId.append(genre["genres"][i]["id"])
        return self.genreId


    #Effettuo più richieste per ottenere più pagine (ogni pagina contiene 20 film)
    def getAllPageMovie(self):
        time.sleep(1)
        movies = {'movies':[]}
        for i in self.genreId:
            count = 1
            flag = True
            while(flag):
                querystring = {'with_genres':i,'page':count}
                resp = self.getSinglePageMovie(querystring)
                print(resp)
                if(resp == {'message':'exit'}):
                    flag = False
                elif(resp == {'message':'wait'}):
                    wait_flag = True
                    jsonString = json.dumps(movies)
                    jsonFile = open(self.path_index, "w")
                    jsonFile.write(jsonString)
                    jsonFile.close()

                    time.sleep(5)
                else:
                    for i in range(19):
                        try:
                            obj = {'id':resp["results"][i]["id"],'title':resp["results"][i]["title"],'release_date':resp["results"][i]["release_date"].split('-')[0],'overview':resp["results"][i]["overview"]}
                        except KeyError:
                            obj = {'id':resp["results"][i]["id"],'title':resp["results"][i]["title"],'release_date':'0000','overview':resp["results"][i]["overview"]}
       
                        movies["movies"].append(obj)                   
                count += 1
                time.sleep(1)
        jsonString = json.dumps(movies)
        jsonFile = open(self.path_index, "w")
        jsonFile.write(jsonString)
        jsonFile.close()

    def readIndex(self):
        data = open(self.path_index)
        movies = json.load(data)
        #print(len(movies["movies"]))
        return movies

#print(response.text)
#test = movie_search()
#test.getGenre()
#print(test.getGenrId())
#time.sleep(1)
#print(test.getSinglePageMovie({'with_genres': 80, 'page': 1}).json()["results"][0]["title"])
#test.getAllPageMovie()
#test.readIndex()
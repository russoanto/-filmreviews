import requests
import json
from bs4 import BeautifulSoup
from concurrent import futures
import hashlib
import os

class index_film:

    def __init__(self,url="https://en.wikipedia.org/wiki/List_of_films:_",path='./index/final_index.json', path_inter='./index/intermediate_index.txt',save_path='./index/resume.txt',max=100000,num_film=0):
        self.URL = url
        self.PATH = path
        self.PATH_INTER = path_inter
        self.MAX_NUM= max
        self.num_film = num_film
        self.save_path = save_path

    
    def save_index(self):
        with open(self.save_path, "w") as openfile:
            openfile.write(self.URL+" "+self.PATH+" "+self.PATH_INTER+" "+ str(self.MAX_NUM)+" "+str(self.num_film))

    @staticmethod
    def resume_index():
        save_path = "./index/resume.txt"

        if os.path.exists(save_path):
            resume_file = open(save_path,'r')
            line = resume_file.readline()
            return line
        else:
            return Noneresponse

    def get_num_film(self):
        return self.num_film

    def id_generator(self):
        for i in range(self.MAX_NUM):
            yield i

    def get_path(self):
        return self.PATH

    def save_result(self, response:str) -> None:
            with open(self.PATH_INTER, "a") as openfile:
                openfile.write(response)

                #for i in range(len(response["results"])):
                    #openfile.write('"' + response["results"][i]["id"] + '"' + ':' +  '"' + response["results"][i]["title"] + '"' +', \n')


    def select_movie(self,char:chr, URL:str) -> None:
        url = self.URL + str(char)
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        for i in soup.find_all('div', class_="div-col"):
            self.save_result(i.get_text())
            #films.add(i.get_text())


    def download_movies(self,ranges:list[str]) -> int :
            with futures.ThreadPoolExecutor(max_workers=10) as executor:
                to_do = []
                for letter in ranges:
                    future = executor.submit(self.select_movie,letter, self.URL)
                    to_do.append(future)
                    msg = 'Scheduled for {}: {}'
                    print(msg.format(letter, future))
                
                results = []
                for future in futures.as_completed(to_do):
                    res = future.result()
                    msg = '{} result: {}'
                    print(msg.format(future,res))
                    results.append(res)
            return len(results)
    
    #TODO Eliminare i caratteri strani tipo \e034f, sono sempre 5 caratteri dopo il back slash (facile da fare)

    def index_json(self,id_gen):
        index = {}
        fields = ["name","year"]
        completed_lines_hash = set()

        for line in open(self.PATH_INTER, "r"):
            if line.find("series:") == -1:
                hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()

                if hashValue not in completed_lines_hash:
                    tmp_dict = {}
                    tmp = 0
                    elem = list(line.strip().split('(',2))
                    if len(elem) == 2:
                        for i in elem:
                            if(tmp == 0):
                                i = i.replace(':','')
                            else:
                                i = i.replace(')','')
                            
                            i = i[::-1].replace(' ','',1)[::-1]
                            tmp_dict[fields[tmp]] = i
                            tmp += 1

                        completed_lines_hash.add(hashValue)
                        id = next(id_gen)
                        index[id] = tmp_dict

        output_file = open(self.PATH, "w")
        json.dump(index, output_file, indent=2, sort_keys=False)
        output_file.close()

    def create_index(self) -> int:
        id_gen = self.id_generator()
        with open(self.PATH,'w') as f:
            f.write('')
        with open(self.PATH_INTER,'w') as f:
            f.write('')
        
        alpha_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','numbers']
        self.download_movies(alpha_string)
        self.index_json(id_gen)
        self.num_film = next(id_gen)-1
        return self.num_film
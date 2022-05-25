import requests
import json
from bs4 import BeautifulSoup
from concurrent import futures
import hashlib

URL = "https://en.wikipedia.org/wiki/List_of_films:_"
PATH = './index/final_index.json'
PATH_INTER = './index/intermediate_index.txt'

MAX_NUM = 100000

films =set()

def id_generator():
    for i in range(MAX_NUM):
        yield i

def get_path():
    return PATH

def save_result(response:str) -> None:
        with open(PATH_INTER, "a") as openfile:

            openfile.write(response)
            #for i in range(len(response["results"])):
                 #openfile.write('"' + response["results"][i]["id"] + '"' + ':' +  '"' + response["results"][i]["title"] + '"' +', \n')


def select_movie(char:chr, URL:str) -> None:
    URL += str(char)
    soup = BeautifulSoup(requests.get(URL).content, 'html.parser')
    for i in soup.find_all('div', class_="div-col"):
        save_result(i.get_text())
        #films.add(i.get_text())


def download_movies(ranges:list[str]) -> int :
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for letter in ranges:
                future = executor.submit(select_movie,letter, URL)
                to_do.append(future)
                msg = 'Scheduled for {}: {}'
                print(msg.format(letter, future))
            
            results = []
            for future in futures.as_completed(to_do):
                res = future.result()
                msg = '{} result: {}'
                print(msg.format(future,res))
                results.append(res)
        print(len(films))
        return len(results)


def index_json(id_gen):
    index = {}
    fields = ["name","year"]
    completed_lines_hash = set()

    for line in open(PATH_INTER, "r"):
        if line.find("series:") == -1:
            hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()

            if hashValue not in completed_lines_hash:
                tmp_dict = {}
                tmp = 0
                if len(list(line.strip().split('(',2))) == 2:
                    for i in list(line.strip().split('(',2)):
                        if(tmp == 0):
                            i = i.replace(':','')
                        else:
                            i = i.replace(')','')
                        tmp_dict[fields[tmp]] = i
                        tmp += 1

                    completed_lines_hash.add(hashValue)
                    id = next(id_gen)
                    index[id] = tmp_dict

    output_file = open(PATH, "w")
    json.dump(index, output_file, indent=2, sort_keys=False)
    output_file.close()


def create_index() -> int:
    id_gen = id_generator()
    with open(PATH,'w') as f:
        pass
    alpha_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','numbers']
    download_movies(alpha_string)
    index_json(id_gen)
    return next(id_gen)-1
    #save_result(str(films))

#create_index()
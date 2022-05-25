import requests
import json
from bs4 import BeautifulSoup
from concurrent import futures
import hashlib

URL = "https://en.wikipedia.org/wiki/List_of_films:_"
PATH = './final_index.json'
PATH_INTER = './intermediate_index.txt'

MAX_NUM = 100000

films =set()

def id_generator():
    for i in range(MAX_NUM):
        yield i


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


def normalize_index(id_gen):
    index = {}
    
    completed_lines_hash = set()

    for line in open(PATH_INTER, "r"):
        if line.find("series:") == -1:
            hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()

            if hashValue not in completed_lines_hash:
                name = list((line.strip().split('(',2)))[0]
                year = list((line.strip().split('(',2)))[1]
                year = year.replace(')','') # for future uses

                name = name.replace(':','')
                id = next(id_gen)
                index[id] = name


                completed_lines_hash.add(hashValue)

    output_file = open(PATH, "w")
    json.dump(index, output_file, indent=4, sort_keys=False)
    output_file.close()


def update_index() -> None:
    id_gen = id_generator()
    with open(PATH,'w') as f:
        pass
    alpha_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','numbers']
    download_movies(alpha_string)
    normalize_index(id_gen)
    #save_result(str(films))

update_index()

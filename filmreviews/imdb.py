import asyncio
import datetime
import requests
import json
import os
from dataclasses import dataclass
from concurrent import futures
import numpy as np


URL = 'https://imdb-api.com'
KEY = 'k_16ywfr35'
        
if not os.path.exists("./imdb/movies"):
    os.mkdir("./imdb/movies")

class Imdb:
    def __init__(self, key, base_url, query_type):
        self.key = key
        self.query_type = query_type
        self.base_url = base_url + '/' + query_type + '/' + self.key + '?' 

    def save_result(self,response):
        path = './imdb/movies/index.json'

        with open(path, "a") as openfile:
            openfile.write(json.dumps(response))

    def send_request(self, url):
        print(url)
        response = requests.get(url).json()
        print(response["results"])
        self.save_result(response)

    def downlioad_movies_date_range(self, date_range) -> int:
        date = np.arange(date_range[0],date_range[1]+1, 2)
        print(date)
       
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for year in date:
                param = ['release_date='+str(year)+'-01-01',str(year+1)+'-12-31','count=250','sort=movimeter,desc']
                future = executor.submit(Imdb.send_request,self,self.base_url + '&'.join(param))
                to_do.append(future)
                msg = 'Scheduled for {}: {}'
                print(msg.format(year, future))
            
            results = []
            for future in futures.as_completed(to_do):
                res = future.result()
                msg = '{} result: {}'
                print(msg.format(future,res))
                results.append(res)

        return len(results)





obj = Imdb(KEY, URL, 'API/AdvancedSearch') 
#print(obj.send_request(['release_date=1960-01-01,1961-12-31','count=250','sort=movimeter,desc']))
obj.downlioad_movies_date_range([1960,2021])


import asyncio
import os
import datetime
import requests
from typing import List
import json
import dataclasses
from dataclasses import dataclass


NAME = 'nytimes'

URL =  'https://api.nytimes.com/svc/search/v2/articlesearch.json'
API_KEY = 'SFXLikyzRO7ZaGerHAkVDiLXtHCh3XfG'


@dataclass
class NyTimesReview:
    id : int
    name : str
    review : str
    actor : List[str]
    director : List[str]
    release_date : datetime




class NyTimesAccess:
    def __init__(self,key,url):
        self.key = key
        self.base_url = url
    
    def retrive_article(self):
        url = self.base_url + '?api-key='+self.key 
        response = request.get(url)
        print(response)
        


access = NyTimesAccess(API_KEY, URL)
    


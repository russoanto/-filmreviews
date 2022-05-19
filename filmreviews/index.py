import requests
import json
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_films:_"

def create_index(char, URL):
    URL += str(char)
    count = 0
    soup = BeautifulSoup(requests.get(URL).content, 'html.parser')
    for i in soup.find_all('div', class_="div-col"):
        print(i.get_text())
        count += 1
    return count

alpha_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ic = 0
for c in alpha_string:
    ic += create_index(c, URL)
print(ic)

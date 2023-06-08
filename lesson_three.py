import os
import requests
from typing import List, Dict, Union

if not os.path.exists("cats"):
    os.makedirs("cats")
    
link = "https://api.thecatapi.com/v1/images/search?limit=10"

a: List[int] = []

answer: List[Dict[str, Union[str, int]]] = requests.get(link).json()

print(answer)

for i in range(10):
    img_url = answer[i]['url']
    img = requests.get(img_url).content
    format = img_url[-3:]
    print(len(img))
    with open(f'cats/cat{i+1}.{format}', 'wb') as file:
        file.write(img)

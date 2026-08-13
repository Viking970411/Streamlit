import requests
from bs4 import BeautifulSoup
url = 'https://aid.mcee.go.kr/negis/list/wa_list_impermeable_ratio.jsp?type=div_table&ctgr=undefined&adm_code=&year=undefined'
import pandas as pd

response = requests.post(url)
print(response.status_code)
#print(response.text)
soup = BeautifulSoup(response.text, 'html.parser')

ros = soup.select('tr')
print(len(ros))

print('tr' in response.text)

print(ros[0].select_one('tr td').text)
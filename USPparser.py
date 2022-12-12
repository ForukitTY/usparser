import re
import requests
from bs4 import BeautifulSoup

url = 'https://usp.kbsu.ru/getinfo.php'
req = requests.post(url, data={'c_fam': "Гедгафов", 'tabn': "1901626"})


def sem_parser(req, semestr=-1):
    soup = BeautifulSoup(req, 'html.parser')

    try:
        table = soup.find_all('table')[semestr]
    except:
        return 'Такого семестра нет'
    PREDMET_ID = 1
    PREPOD_ID = 2
    ITOG_ID = -2
    pars_line = ''
    for row in table.find_all('tr')[3:]:
        line = row.find_all('td')
        pars_line += line[PREDMET_ID].text.strip() + '-' + line[PREPOD_ID].text.strip() + ' ' + line[
            ITOG_ID].text.strip() + ':white_check_mark: \n'

    return pars_line


sem_parser(req.text)

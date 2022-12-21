from bs4 import BeautifulSoup


def sem_parser(req, semestr=0):
    soup = BeautifulSoup(req, 'html.parser')

    try:
        table = soup.find_all(attrs={"class": "clTableBold"})[semestr-1]
    except:
        return 'Такого семестра нет'
    PREDMET_ID = 0
    PREDMET = 1
    PREPOD_ID = 2
    ITOG_ID = -2
    pars_line = ''
    for row in table.find_all('tr')[2:]:
        line = row.find_all('td')
        line_mark = line[ITOG_ID].text.strip()
        pars_line += line[PREDMET_ID].text.strip() + '. ' + line[PREDMET].text.strip() + ' - ' + line[PREPOD_ID].text.strip() + ' |' + line_mark + ('| ✅ \n' if int(line_mark) > 60 else '| 🛑\n')

    return pars_line

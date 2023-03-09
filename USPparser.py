from bs4 import BeautifulSoup
# TODO: жирный шрифт и чуть более понятное выделение текста


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
    parsed_line = ''
    for row in table.find_all('tr')[2:]:
        cells = row.find_all('td')
        list_control_points = row.find_all(attrs={"class": "cltdb"})[:3]
        line_mark = cells[ITOG_ID].text.strip()
        parsed_line += cells[PREDMET_ID].text.strip() + '. ' + cells[PREDMET].text.strip() + ' - ' + cells[PREPOD_ID].text.strip() \
                       + ' | \n' + str([int(control_mark_i.text) for control_mark_i in list_control_points]) + ' Итог: ' + line_mark + ('  ✅\n\n' if int(line_mark) > 60 else '  🛑\n\n')

    return parsed_line

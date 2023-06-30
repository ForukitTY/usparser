from bs4 import BeautifulSoup
# TODO: оценку на экзаменах
# TODO: если студен восстановившийся, бот работает некорректно


def sem_parser(req, semestr=0):
    soup = BeautifulSoup(req, 'html.parser')

    try:
        tables = soup.find_all(attrs={"class": "clTableBold"})
        semestr_count_by_user = len(tables)
        table = tables[semestr-1]
    except:
        return 'Такого семестра нет'
    PREDMET_ID = 0
    PREDMET_NAMES = 1
    PREPOD_ID = 2
    ITOG_ID = -2
    parsed_line = ''
    for row in table.find_all('tr')[2:]:
        cells = row.find_all('td')
        list_control_points = row.find_all(attrs={"class": "cltdb"})[:3]
        predmet_number_iter = cells[PREDMET_ID].text.strip()
        ekzamen_name_type_list = cells[PREDMET_NAMES].text.strip().split('\n')
        predmet_name = ekzamen_name_type_list[0]
        ekzamen_type = ekzamen_name_type_list[1] if len(ekzamen_name_type_list) > 1 else ""
        prepod_name = cells[PREPOD_ID].text.strip()
        itog_mark = cells[ITOG_ID].text.strip()

        parsed_line += predmet_number_iter + '. ' + predmet_name + '\n' +\
                       ekzamen_type + prepod_name + '\n' +\
                       str([int(control_mark_i.text) for control_mark_i in list_control_points]) + \
                       ' Итог: ' + itog_mark + ('  ✅\n\n' if int(itog_mark) > 60 else '  🛑\n\n')

    return parsed_line

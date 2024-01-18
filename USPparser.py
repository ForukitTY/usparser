from bs4 import BeautifulSoup
# TODO: если студен восстановившийся, бот работает некорректно


def sem_parser(req, semestr=0):
    soup = BeautifulSoup(req, 'html.parser')

    try:
        tables = soup.find_all(attrs={"class": "clTableBold"})  # ['ttable1', .., , ,]
        # semestr_count_by_user = len(tables)
        table = tables[semestr-1]
    except:
        return 'Такого семестра нет'

    PREDMET_ID = 0
    PREDMET_NAMES = 1
    PREPOD_ID = 2
    ITOG_ID = -2
    ZACHET_ROW_ID = -6
    EKZAMEN_ROW_ID = -5
    parsed_line = ''
    for row in table.find_all('tr')[2:]:
        cells = row.find_all('td')
        list_control_points = row.find_all(attrs={"class": "cltdb"})[:3]
        predmet_number_iter = cells[PREDMET_ID].text.strip()
        ekzamen_name_type_list = cells[PREDMET_NAMES].text.strip().split('\n')
        predmet_name = ekzamen_name_type_list[0]
        exam_type = ekzamen_name_type_list[1] if len(ekzamen_name_type_list) > 1 else ""
        prepod_name = cells[PREPOD_ID].text.strip()
        itog_mark = cells[ITOG_ID].text.strip()
        was_session = False
        if cells[ZACHET_ROW_ID].text.strip():
            session_mark = f"+'{cells[ZACHET_ROW_ID].text.strip()}' (за зачет)"
            was_session=True
        elif cells[EKZAMEN_ROW_ID].text.strip():
            session_mark = f"+'{cells[EKZAMEN_ROW_ID].text.strip()}' (за экзамен)"
            was_session=True
        else:
            session_mark = "+'0' (баллов за зачет/экзамен нет)"

        parsed_line += predmet_number_iter + '. ' + predmet_name + '\n' +\
                       exam_type + prepod_name + '\n' +\
                       str([int(control_mark_i.text) for control_mark_i in list_control_points]) + f"{session_mark}" +\
                       ' Итог: ' + itog_mark + ('  ✅\n\n' if int(itog_mark) > 60 and was_session else '  🛑\n\n')

    return parsed_line

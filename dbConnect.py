import os
import sqlite3
import logging


def add_to_db(tg_id: int, surname: str, za4etka: int):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "TGUsers.db")
    connect = sqlite3.connect(db_path)
    cursos = connect.cursor()
    data = [tg_id, surname, za4etka]
    try:
        cursos.execute("""INSERT INTO Users (tgID, surname, bookNumber) VALUES (?,?,?);""", data)
        logging.info(f"[DB ADD] {data}")
    except:
        cursos.execute("""UPDATE Users set surname=?, bookNumber =? WHERE tgID = ?;""", (surname, za4etka, tg_id))
        logging.info(f"[DB UPDATE] {data}")
        print(f'Обновили данные для {tg_id}, {surname}')

    connect.commit()
    cursos.close()


def get_from_db(tg_id: int) -> tuple:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "TGUsers.db")
    connect = sqlite3.connect(db_path)
    cursos = connect.cursor()
    cursos.execute(f"""SELECT surname, bookNumber FROM Users WHERE tgID={tg_id}""")
    records = cursos.fetchall()
    cursos.close()
    try:
        usp_login_data = records[0]
        logging.info(f"[DB GET SUCCESS] by user {tg_id}")
        return usp_login_data
    except:  # если пользователь не найден в базе
        logging.info(f"[DB GET EMPTY] by user {tg_id}")
        return None, None

def users_count():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "TGUsers.db")
    connect = sqlite3.connect(db_path)
    cursos = connect.cursor()
    cursos.execute(f"""SELECT Count(*) FROM Users""")
    return cursos.fetchone()[0]

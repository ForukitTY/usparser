import sqlite3


def add_to_db(tg_id: int, surname: str, za4etka: int):
    connect = sqlite3.connect(r'C:\sqliteDBs\TGUsers.db')
    cursos = connect.cursor()
    data = [tg_id, surname, za4etka]
    try:
        cursos.execute("""INSERT INTO Users (tgID, surname, bookNumber) VALUES (?,?,?);""", data)
    except:
        cursos.execute("""UPDATE Users set surname=?, bookNumber =? WHERE tgID = ?;""", (surname, za4etka, tg_id))
        print(f'Обновили данные для {tg_id}, {surname}')

    connect.commit()
    cursos.close()


def get_from_db(tg_id: int) -> tuple:
    connect = sqlite3.connect(r'C:\sqliteDBs\TGUsers.db')
    cursos = connect.cursor()
    cursos.execute(f"""SELECT surname, bookNumber FROM Users WHERE tgID={tg_id}""")
    records = cursos.fetchall()
    cursos.close()
    try:
        return records[0]
    except:
        return None, None

# закрывать ли подключение к базе?
# connect = sqlite3.connect(r'C:\sqliteDBs\TGUsers.db')
# cursos = connect.cursor()
# cursos.execute(f"""INSERT INTO Users (tgID, surname, bookNumber) VALUES (2, "гедгафов", 123)""")
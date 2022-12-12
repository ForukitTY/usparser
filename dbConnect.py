import sqlite3


def add_to_db(tg_id :int, surname: str, za4etka: int):

    connect = sqlite3.connect(r'C:\sqliteDBs\TGUsers.db')
    cursos = connect.cursor()
    cursos.execute(f"""INSERT INTO Users ('tgID', 'surname', 'bookNumber') VALUES({tg_id},{surname},{za4etka})""")
    connect.commit()

#закрывать ли подключение к базе?
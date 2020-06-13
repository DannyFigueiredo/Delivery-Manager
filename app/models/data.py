import sqlite3

db = sqlite3.connect('storage.db')


db.execute("""INSERT INTO users(username, password, level, available)
values ('adm', '201020', 'manager', 1)""")
print('Usuário inserido com sucesso.')

db.commit()
print('Para finalizar aquele commit espereto!')

db.close()
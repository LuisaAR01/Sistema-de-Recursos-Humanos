import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT id, username, password, rol FROM usuarios")

usuarios = cursor.fetchall()

for u in usuarios:
    print(u)

conn.close()
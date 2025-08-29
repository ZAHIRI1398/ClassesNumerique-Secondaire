import sqlite3

conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()
cursor.execute("SELECT id, title, exercise_type FROM exercise WHERE exercise_type = 'flashcards'")
results = cursor.fetchall()
print("Exercices de type flashcards trouvés :")
for row in results:
    print(f"ID: {row[0]}, Titre: {row[1]}")
conn.close()

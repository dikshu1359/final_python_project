import sqlite3

# Connect to a database (or create it if it doesn't exist)
conn = sqlite3.connect("my_database.db")

# Create a table
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")

# Insert a user
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))

# Save changes
conn.commit()

# Fetch and print data
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

# Close the connection
conn.close()

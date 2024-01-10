import sqlite3

# Connect to the SQLite database or create it if it doesn't exist
conn = sqlite3.connect('my_database.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Define an SQL statement to create a table with 'Status' and 'Vehicle Number' columns
create_table_query = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    status TEXT NOT NULL,
    vehicle_number TEXT NOT NULL
);
'''

# Execute the SQL statement to create the table
cursor.execute(create_table_query)

# Commit the changes to the database and close the connection
conn.commit()
conn.close()

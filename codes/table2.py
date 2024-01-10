import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('my_database.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Define an SQL query to select data from a table (e.g., 'users')
select_query = "SELECT * FROM users"

# Execute the SQL query
cursor.execute(select_query)

# Fetch the data from the cursor
data = cursor.fetchall()

# Close the database connection
conn.close()

# Now 'data' contains the results of the query, which you can process as needed
for row in data:
    print("Data")
    print(row)

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import cv2
import imutils
import pytesseract
import pandas as pd
import os
import re

app = Flask(__name__)
app.secret_key = '12345'

    
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('login.html')



# Route to render the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            # Save user details in the session
            session['user_id'] = user[0]
            session['username'] = user[1]  # Assuming the username is in the second column
            session['status'] = user[3]  # Assuming the status is in the fourth column
            session['vehicle_number'] = user[4]  # Assuming the vehicle number is in the fifth column
            return render_template('dashboard.html', username=session['username'], status=session['status'], vehicle_number=session['vehicle_number'])
        else:
            return 'Invalid username or password'

    return render_template('login.html')

# Define a route for the dashboard

@app.route('/signup', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        # Extract data from the form
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        vehicle_number = request.form['vehicle_number']
        status = request.form['status']

        # Connect to the SQLite database
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

        # Insert user data into the database
        cursor.execute("INSERT INTO users (username, password, vehicle_number, status) VALUES (?, ?, ?, ?)",
                       (username, password, vehicle_number, status))
        
        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Redirect to a success page or handle other logic as needed
        return render_template('login.html')

    # Render a response page (optional)
    return render_template('signup.html')


@app.route('/admin')
def admin():
    if 'username' in session and session['status'] == 'Admin':
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

        # Retrieve user data from the database
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        conn.close()

        return render_template('admin.html', users=users)
    else:
        return 'Unauthorized access'

# Route to handle status updates
@app.route('/update_status/<int:user_id>', methods=['POST'])
def update_status(user_id):
    if 'username' in session and session['status'] == 'Admin':
        new_status = request.form['new_status']

        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

        # Update the user's status in the database
        cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
        conn.commit()

        conn.close()

        # Redirect back to the admin page after updating
        return redirect(url_for('admin'))
    else:
        return 'Unauthorized access'


# Route to process the selected image
@app.route('/process_image', methods=['POST'])

def process_image():
    # Receive the uploaded image from the form
    uploaded_image = request.files['image']

    if not uploaded_image:
        return "No image uploaded."

    # Define a path to temporarily save the uploaded image
    image_path = 'temp_image.jpg'

    # Save the uploaded image to the server
    uploaded_image.save(image_path)

    # Now, you can pass the image path to your OCR code
    result = run_ocr(image_path)

    # Delete the temporary image file
    os.remove(image_path)

    return "OCR Result: " + result

def run_ocr(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if image is None:
        return "Error: Unable to load the image. Check the file path and integrity."

    # Resize the image
    image = imutils.resize(image, width=500)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    

    edged = cv2.Canny(gray, 170, 200)

    # Find contours
    contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and keep the largest ones
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

    NumberPlateCnt = None

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            NumberPlateCnt = approx
            break

    # Check if a valid contour was found
    if NumberPlateCnt is not None:
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [NumberPlateCnt], 0, 255, -1)
    else:
        return "No number plate detected."
    
    new_image = cv2.bitwise_and(image, image, mask=mask)

    # Configuration for Tesseract
    config = ('-l eng --oem 1 --psm 3')

    # Run Tesseract OCR on the image
    text = pytesseract.image_to_string(new_image, config=config)

    # Return the OCR result

    # Remove all empty spaces (whitespace) from the OCR result
    
    text = re.sub(r'[^a-zA-Z0-9]', '', text)

    conn = sqlite3.connect('my_database.db')  # Replace with your database path
    cursor = conn.cursor()

    cursor.execute("SELECT username, status FROM users WHERE vehicle_number = ?", (text,))
    user_info = cursor.fetchone()

    conn.close()

    if user_info:
        username, status = user_info
        return f"User: {username}, Status: {status}"
    else:
        return "Vehicle number not found in the database."

@app.route('/check_vehicle_number', methods=['POST'])
def check_vehicle_number():
    # Receive the manually entered vehicle number from the form
    manual_vehicle_number = request.form['manual_vehicle_number']

    # Remove all characters that are not numbers or alphabets
    manual_vehicle_number = re.sub(r'[^a-zA-Z0-9]', '', manual_vehicle_number)

    # Check if the manually entered vehicle number is present in the database
    conn = sqlite3.connect('my_database.db')  # Replace with your database path
    cursor = conn.cursor()

    cursor.execute("SELECT username, status FROM users WHERE vehicle_number = ?", (manual_vehicle_number,))
    user_info = cursor.fetchone()

    conn.close()

    if user_info:
        username, status = user_info
        return f"User: {username}, Status: {status}"
    else:
        return "Vehicle number not found in the database."


if __name__ == "__main__":
    app.run(debug=True)



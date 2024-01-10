import numpy as np
import cv2
import imutils
import sys
import pytesseract
import pandas as pd

# Load the image
path = "Enter Path Here"
image = cv2.imread(path)

# Check if the image was loaded successfully
if image is None:
    print("Error: Unable to load the image. Check the file path and integrity.")
    sys.exit(1)

# Resize the image
image = imutils.resize(image, width=500)

cv2.imshow("Original Image", image)

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
    print("No number plate detected.")
    text = input("Enter the number plate manually: ")

new_image = cv2.bitwise_and(image, image, mask=mask)
cv2.namedWindow("Final_image", cv2.WINDOW_NORMAL)
cv2.imshow("Final_image", new_image)

# Configuration for tesseract
config = ('-l eng --oem 1 --psm 3')

# Run Tesseract OCR on the image
text = pytesseract.image_to_string(new_image, config=config)

# Prompt the user to confirm the detected number plate or manually entered number plate
while True:
    user_response = input("Detected/Entered number plate: {}. Is this correct? (yes/no): ".format(text))
    if user_response.lower() in ['yes', 'no']:
        break
    else:
        print("Invalid response. Please enter 'yes' or 'no'.")

if user_response.lower() == 'no':
    text = input("Enter the correct number plate: ")

# Prompt the user for username and ID
username = input("Enter username: ")
id_number = input("Enter ID: ")

# Data to be stored in the CSV file
raw_data = {
    'v_number': [text],
    'username': [username],
    'id': [id_number]
}

df = pd.DataFrame(raw_data, columns=['v_number', 'username', 'id'])

# Append to the CSV file or create a new one if it doesn't exist
with open('data.csv', 'a') as f:
    df.to_csv(f, header=f.tell()==0, index=False)

# Print recognized text
print("Data successfully added to the CSV file.")

cv2.waitKey(0)

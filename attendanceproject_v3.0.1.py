import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from datetime import date
import csv
from email.message import EmailMessage
import ssl
import smtplib

# Path to the directory containing student images
path = "C:/Attend-Ease/Attend-Ease/Student DataBase"

# Check if the directory exists, and create it if it doesn't
if not os.path.exists(path):
    try:
        os.makedirs(path)
    except PermissionError:
        print(f"PermissionError: Unable to create directory {path}. Check permissions.")
        # Add additional handling as needed

# Load student images and names
stud_db = []
studNames = []

studList = os.listdir(path)
for stud in studList:
    currentImg = cv2.imread(os.path.join(path, stud))
    stud_db.append(currentImg)
    studNames.append(os.path.splitext(stud)[0])


def send_mail(receiver):
    email_sender = 'attendease05@gmail.com'
    email_password = 'hcob uwpc rsrb djue'
    email_receiver = receiver

    subject = 'Attendance Recorded'
    body = f"""
    Date: {date.today()}
    Time: {datetime.now().strftime('%H:%M:%S')}
    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def find_encodings(stud_img):
    encode_list = []
    for stud in stud_img:
        stud = cv2.cvtColor(stud, cv2.COLOR_BGR2RGB)
        cv2.imshow('Image', stud)
        cv2.waitKey(100)
        encode = face_recognition.face_encodings(stud)[0]
        encode_list.append(encode)

    return encode_list


def mark_attendance(stud_name, time):
    stud_name = stud_name.lower()
    dir = "C:/Attend-Ease/Attend-Ease/Attendance"
    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except PermissionError:
            print(f"PermissionError: Unable to create directory {dir}. Check permissions.")
            # Add additional handling as needed

    filename = str(date.today())
    dir = os.path.join(dir, filename)
    filename = filename + '-' + time
    filename = filename + ".csv"
    dir = os.path.join(dir, filename)

    if not os.path.exists(os.path.dirname(dir)):
        os.makedirs(os.path.dirname(dir))

    with open(dir, 'a+') as f:
        f.seek(0)
        my_stud_list = f.readlines()
        stud_name_list = []
        for line in my_stud_list:
            entry = line.split(',')
            stud_name_list.append(entry[0])
        if stud_name not in stud_name_list:
            timestr = datetime.now().strftime('%H:%M:%S')
            f.writelines(f"\n{stud_name},{timestr}")

            stud_email = []
            email_loc = "C:/Attend-Ease/Attend-Ease/email.csv"
            # Check if the directory exists, and create it if it doesn't
            if not os.path.exists(email_loc):
                try:
                    os.makedirs(email_loc, exist_ok=True)
                except PermissionError:
                    print(f"PermissionError: Unable to create directory {email_loc}. Check permissions.")
                    # Add additional handling as needed

            with open(email_loc) as em:
                email_data = csv.reader(em, delimiter=',')
                next(email_data)
                for row in email_data:
                    stud_email.append(row)

            for row in stud_email:
                if stud_name == row[0]:
                    send_mail(row[1])
                    break


encode_list_known = find_encodings(stud_db)

stud = cv2.VideoCapture(0, cv2.CAP_DSHOW)

dir = "C:/Attend-Ease/Attend-Ease/Attendance/"

# Check if the directory exists, and create it if it doesn't
if not os.path.exists(dir):
    try:
        os.makedirs(dir)
    except PermissionError:
        print(f"PermissionError: Unable to create directory {dir}. Check permissions.")
        # Add additional handling as needed

filename = str(date.today())
dir = os.path.join(dir, filename)

# Check if the directory exists, and create it if it doesn't
if not os.path.exists(dir):
    try:
        os.makedirs(dir)
    except PermissionError:
        print(f"PermissionError: Unable to create directory {dir}. Check permissions.")
        # Add additional handling as needed

col_header = ["Name", "Time"]

time = datetime.now().strftime('%H-%M-%S')
filename = filename + '-' + time
filename = filename + ".csv"

with open(os.path.join(dir, filename), "w") as f:
    studList = csv.writer(f)
    studList.writerow(col_header)

while True:
    success, stud_img = stud.read()
    stud_img_s = cv2.resize(stud_img, (0, 0), None, 0.25, 0.25)

    stud_face_loc = face_recognition.face_locations(stud_img_s)
    stud_encode = face_recognition.face_encodings(stud_img_s, stud_face_loc)

    for encode_stud, face_loc_stud in zip(stud_encode, stud_face_loc):
        matches = face_recognition.compare_faces(encode_list_known, encode_stud)
        face_dis = face_recognition.face_distance(encode_list_known, encode_stud)
        match_index = np.argmin(face_dis)

        if matches[match_index]:
            name = studNames[match_index].upper()
            y1, x2, y2, x1 = face_loc_stud
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(stud_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(stud_img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(stud_img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            mark_attendance(name, time)
        else:
            name = 'Unknown'
            y1, x2, y2, x1 = face_loc_stud
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(stud_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(stud_img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(stud_img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Input", stud_img)
    if cv2.waitKey(1) & 0xFF == ord('`'):
        break

# Release the video capture object and close all OpenCV windows
stud.release()
cv2.destroyAllWindows()

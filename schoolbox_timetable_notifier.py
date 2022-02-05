from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from win10toast import ToastNotifier
#from PIL import Image
import time
import getpass
from selenium.webdriver.chrome.service import Service

# Set options.headless to False to see chrome browser - Useful for debugging
options = Options()
options.headless = True

s = Service('C:/Windows/chromedriver.exe')

driver = webdriver.Chrome(options=options, service=s)

signinurl = 'https://adfs.tareeccs.nsw.edu.au/adfs/ls/?SAMLRequest=jVNNj9owEL3zK1Du5GuzbGpBJBb6gUQhgmwPvayMMymWHDv1OIX%2B%2BzoOW9BqF60vkd7Me573PJkgrUVDZq05yC38bgHNYGjPqRYSiStOvVZLoihyJJLWgMQwspt9X5HYD0mjlVFMCe8V7TaLIoI2XMmetlxMvc3682rzdbl%2B3ldRuqfjcJyMY3ofxZ%2BSaJxEADGFrnJ3%2F5Ckd5CmPfUHaLQ6U8%2FKeoNeDbGFpURDpbF4GMejMBrFaRFGJHkgSfKzpy6sWS6pcfSDMQ2SIKBlhb6hGoAx9CUefShbn7auEAgMem5%2Btv3IZcnlr9tu930Tkm9FkY%2Fyza7oRWYvKcyVxLYGvQP9hzN42q4uAyE7KCX26vTmVF3UAevpfnNovMwpTzqcuCB09iGlSXBNuYg0ZG39LBe5Epz9dXh3vihdU%2FO%2B7ciPHMLLUeVaSSuxAcYrDqX3X2YmhDrONVADU8%2FoFrxhkF3dfV5JKN2C2pgMnMxwruqGao7du8GJMnN2fXF%2B3T4Xdtu2UGU3F5IR1vVZOLefo9Jl98TA7N2FpnZ2pc05ozfF%2B8SCG2Nng5fy9d%2BW%2FQM%3D&RelayState=%2Flogin%2F&client-request-id=426a145c-e743-4ff4-ad43-0080010000bd&pullStatus=0'
targeturl = 'https://schoolbox.tareeccs.nsw.edu.au/timetable'

username = ""
password = ""

periodtimes = {
    "0830": "morning1",
    "0850": "morning2",
    "0905": "Devotions",
    "0925": "Period1",
    "1020": "Period2",
    "1115": "Recess",
    "1135": "Period3",
    "1230": "Period4",
    "1325": "Lunch1",
    "1345": "Lunch2",
    "1405": "Period5",
    "1501": "Afternoon1",
    "1520": "Afternoon2",
    "1800": "Afternoon3",
    }

periodindex = {
    "morning1": 0,
    "morning2": 10,
    "Devotions": 20,
    "Period1": 30,
    "Period2": 40,
    "Recess": 50,
    "Period3": 60,
    "Period4": 70,
    "Lunch1": 80,
    "Lunch2": 90,
    "Period5": 100,
    "Afternoon1": 110,
    "Afternoon2": 120,
    "Afternoon3": 130
    }
Monday, Tuesday, Wednesday, Thursday, Friday = 0, 1, 2, 3, 4
# A, B = 0, 5

# Signs in and gets html from the timetable page
def update_timetable():
    global subjects
    # Sign in

    print("Logging in...")

    driver.get(signinurl)
    #driver.find_element(By.ID, "idp_SignInButton").click()
    driver.find_element(By.ID, "userNameInput").send_keys(username)
    driver.find_element(By.ID, "passwordInput").send_keys(password)
    driver.find_element(By.ID, "submitButton").click()


    # wait for the ready state to be complete
    WebDriverWait(driver=driver, timeout=10).until(
        lambda x: x.execute_script("return document.readyState === 'complete'")
    )  

    driver.get(targeturl)
    #print(driver.page_source)
    time.sleep(1)

    if driver.current_url == targeturl:
        print("Login successful.")
    else: 
        print("Login failed. Please re-enter your login details")
        ask_for_signin()
        update_timetable()


    soup = BeautifulSoup(driver.page_source, 'html.parser')
    soup.prettify()
    subjects = soup.find_all("div", {"class": "timetable-subject"})

# Ask user for the week on startup
week = 0
def ask_for_week():
    print("")
    print("")
    print("")
    week_found = False
    while week_found == False:
        week_input = input("What week is it? (A or B): ")
        if week_input.upper() == "A":
            week = 0
            week_found = True
        elif week_input.upper() == "B":
            week = 5
            week_found = True
        else:
            print("please input either 'A' or 'B'.")

# Switches weeks at 3pm on Sunday
def switch_weeks():
    global week
    if datetime.today().weekday() == 6 and datetime.now().strftime("%H%M") == "1500":
        if week == "A":
            week = "B"
        elif week == "B":
            week = "A"
        print(f"week changed to {week}.")

def ask_for_signin():
    global username, password
    print("The bot requires your Schoolbox login details so it can access your online timetable.")
    print("When entering your password, the text you enter will not show up. This is just a security feature. ")
    username = input("School email: ")
    password = getpass.getpass(prompt='Password: ')
    cont = False
    while cont == False:
        print("enter 'pass' to check your password. Warning [!Make sure nobody is looking over your shoulder!]")
        print("enter 'retry' to re-enter your login details")
        print("enter 'continue' to continue")
        response = input()
        if response == 'pass':
            print(password, end="\r")
            time.sleep(2)
            print("hidden                                                                      ", end="\r")
        elif response == 'retry':
            username = input("School email: ")
            password = getpass.getpass(prompt='Password: ')
        elif response == 'continue':
            cont = True;
        else:
            print("invalid response")
        

# Converts the time to the correct period using the "periodtimes" dictionary
def getperiod():
    now = datetime.now()
    for key in periodtimes:
        if int(now.strftime("%H%M")) <= int(key):
            return periodtimes[key]


# Converts the period to a number that can be used to find the correct html
def getperiodindex():
    global week
    if datetime.today().weekday() != 5 and datetime.today().weekday() != 6:
        print(subjects[int(periodindex[getperiod()]) + datetime.today().weekday() + week])
        return subjects[int(periodindex[getperiod()]) + datetime.today().weekday() + week]
    else:
        return "Not a School Day!"

# Notification 10 minutes before next period
def prenotify():
    now = datetime.now()
    current_time = str(int(now.strftime("%H%M")) + 10)
    if current_time in periodtimes:
        print("period notification")
        notify = ToastNotifier()
        notify.show_toast(("Next: " + getperiod()),str(getperiodinfo()), icon_path="logo.ico", duration=10)

# Notification on change in periods
def notify():
    now = datetime.now()
    current_time = now.strftime("%H%M")
    if current_time in periodtimes:
        print("period notification")
        notify = ToastNotifier()
        notify.show_toast(getperiod(),str(getperiodinfo()), icon_path="logo.ico", duration=10)

# Finds data from html using period index
def getperiodinfo():
    soup2 = BeautifulSoup(str(getperiodindex()), features="lxml")
    return(soup2.get_text())

print("")
print("")
print("")
ask_for_signin()
ask_for_week()
update_timetable()
driver.close()
print("")
print("")
print("")
print("Initialisation complete")
print("You will get notifications 10 minutes before each class and on the changeover between classes.")
print("Notifications include details such as class name, teacher, and class location, using information avaliable from Schoolbox.")
print("keep this terminal open to keep recieving notifications. I am working on a better solution. ")
print("That also means that if you restart your computer or accidentally close this window, you will have to run the program and login again.")

while True:
    prenotify()
    notify()
    switch_weeks()
    time.sleep(60)

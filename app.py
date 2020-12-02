from __future__ import print_function
from flask import Flask,render_template,request
import os
import pickle
import numpy as np
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email import errors
import base64


#********************************************Gmail API************************************************************#

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


"""Shows basic usage of the Gmail API.
Lists the user's Gmail labels.
"""
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)


#*******************************************----------************************************************************#


payment_amount={}
payment_amount['amount'] = 23200

def check_application_for_rejection(home_salary,additonal_salary,mortgage_value,food_value,transport_value,light_expenditure,water_value,grooming_value,entertainment_value,current_loan_payment,kids_value):
  salary = int(home_salary)
  if(additonal_salary!=""):
    salary = salary + int(additonal_salary)

  expense = int(mortgage_value) + int(food_value) + int(transport_value) + int(light_expenditure) + int(water_value) +int(grooming_value) +int(entertainment_value) + int(kids_value)

  if(current_loan_payment!=""):
    expense = expense + int(current_loan_payment)

  total = salary - expense
  if(total>=payment_amount['amount']):
    return False
  else:
    return True

def prediction_by_model(age,money_borrow,lights_expenditure,martial_status,occupation,working_with_employee,residential_status,living_at_present_address,kids,loan_purpose):
  features = []
  
  features.append(int(age))

  features.append(int(money_borrow))
  features.append(int(lights_expenditure))

  if(martial_status=="married"):
    features.extend([1,0])
  elif(martial_status=="single"):
    features.extend([0,1])
  else:
    features.extend([0,0])

  if(occupation=="Clerk"):
    features.extend([1,0,0])
  elif(occupation=="Others"):
    features.extend([0,1,0])
  elif(occupation=="Sales"):
    features.extend([0,0,1])
  else:
    features.extend([0,0,0])

  if(working_with_employee=="0 to 1year"):
    features.append(1)
  else:
    features.append(0)
  

  if(residential_status=="Living With Parents"):
    features.append(1)
  else:
    features.append(0)
  

  if(living_at_present_address=="10 to 24Years"):
    features.extend([1,0])
  elif(living_at_present_address=="2 to 9Years"):
    features.extend([0,1])
  else:
    features.extend([0,0])

  if(kids=="2"):
    features.append(1)
  else:
    features.append(0)
  
  if(loan_purpose=="Personal"):
    features.append(1)
  else:
    features.append(0)
  
  model = pickle.load(open('loan_estimator.pkl', 'rb'))
  parameters = [features]
  parameters = np.array(parameters)
  prediction = model.predict(parameters)
  if(prediction[0]==1):
    return True
  else:
    return False


app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/index.html",methods=['GET','POST'])
def home_1():
    return render_template('index.html')


@app.route("/form.html",methods=['GET','POST'])
def form_1():
    # print(request.form['payment'])
    payment_amount['amount'] = 23200
    if(request.form['payment']!=""):
        payment_amount['amount'] = int(request.form['payment'])
    return render_template('form.html')


@app.route("/form1.html",methods=['GET','POST'])
def form_2():
    return render_template('form1.html')


@app.route("/end.html",methods=['GET','POST'])
def end_page():

    if(request.method=="POST"):
        check = check_application_for_rejection(request.form['home_salary'],request.form['income_additional'],request.form['mortgage_value'],request.form['food_value'],request.form['transport_value'],request.form['light_expenditure'],request.form['water_value'],request.form['grooming_value'],request.form['entertainment_value'],request.form['current_loan_payment'],request.form['kids_value'])
        if(check ==  False):
          pay_check = prediction_by_model(request.form['user_age'],request.form['moneyBorrow'],request.form['light_expenditure'],request.form['Marital Status'],request.form['occupation_tag'],request.form['working_with_employee'],request.form['Residential Status'],request.form['present address'],request.form['kids'],request.form['LoanPurpose'])
          if(pay_check==True):
              message = MIMEText("Hi. Your application is approved. Go to the followin link to complete the process https://moniready.aidaform.com/moniready-upload-form")
              message['to']=request.form['user_email']
              message['from'] = "syed.ammar.98sep@gmail.com"
              message['subject']="Moniready Application"
              raw = base64.urlsafe_b64encode(message.as_bytes())
              raw = raw.decode()
              body={'raw':raw}
              try:
                  res = (service.users().messages().send(userId="me",body=body).execute())
                  print("your message has been sent")
              except:
                  print("an error occured")
          else:
              message = MIMEText("Sorry. Your application is not approved")
              message['to']=request.form['user_email']
              message['from'] = "syed.ammar.98sep@gmail.com"
              message['subject']="Moniready Application"
              raw = base64.urlsafe_b64encode(message.as_bytes())
              raw = raw.decode()
              body={'raw':raw}
              try:
                  res = (service.users().messages().send(userId="me",body=body).execute())
                  print("your message has been sent")
              except:
                  print("an error occured")
        else:
            message = MIMEText("Sorry. Your application is not approved")
            message['to']=request.form['user_email']
            message['from'] = "syed.ammar.98sep@gmail.com"
            message['subject']="Moniready Application"
            raw = base64.urlsafe_b64encode(message.as_bytes())
            raw = raw.decode()
            body={'raw':raw}
            try:
                res = (service.users().messages().send(userId="me",body=body).execute())
                print("your message has been sent")
            except:
                print("an error occured")
        
    return render_template('end.html')


if __name__ == '__main__':
  app.run(port = int(os.environ.get("PORT", 5000)))


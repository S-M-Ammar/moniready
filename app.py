from __future__ import print_function
from flask import Flask,render_template,request
import os
from datetime import date
import pickle
import numpy as np
import json
from datetime import date
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email import errors
import base64
import store_data

user_dict = {}


#*******************************************Sheet API************************************************************#
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '16ne42-2Sp62SnTw221SPOdCmwJOvBaiq9CJ2apAWTOg'
try:
  sheet_service = store_data.get_sheet_service()
except:
  print("No connection found for google sheets")
#*****************************************************************************************************************#


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


def check_application_for_rejection(home_salary,additonal_salary,mortgage_value,food_value,transport_value,light_expenditure,water_value,grooming_value,entertainment_value,current_loan_payment,kids_value,amount_borrowed,loan_time):
  salary = int(home_salary)
  if(additonal_salary!=""):
    salary = salary + int(additonal_salary)

  expense = int(mortgage_value) + int(food_value) + int(transport_value) + int(light_expenditure) + int(water_value) +int(grooming_value) +int(entertainment_value) + int(kids_value)

  if(current_loan_payment!=""):
    expense = expense + int(current_loan_payment)

  payments = 23200
  amount_borrowed = int(amount_borrowed)
  loan_time = int(loan_time[0])

  try:
    payments = amount_borrowed/loan_time
    interest_rate_amount = 0.16 * amount_borrowed
    payments = payments + interest_rate_amount

    try:
      payments = round(payments,0)
    except:
      pass
  except:
    payments = 23200

  total = salary - expense
  thirty_percent = 0.4 * total
  if(thirty_percent>=payments):
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
    return render_template('form.html')


@app.route("/form.html",methods=['GET','POST'])
def form_1():
    return render_template('form.html')


@app.route("/form1.html",methods=['GET','POST'])
def form_2():
    return render_template('form1.html')


@app.route("/end.html",methods=['GET','POST'])
def end_page():
    application_status = ""
    if(request.method=="POST"):
        user_dict = {}
        x = json.dumps(request.form['params'])
        y = eval(json.loads(x))
        user_dict = y
        check = check_application_for_rejection(y['salary'],y['additional_salary'],y['mortgage_expense'],y['food_expense'],y['transportation_expense'],y['light_expense'],y['water_expense'],y['grooming_expense'],y['entertainment_expense'],y['exist_loan_amount'],y['kids_expense'],y['amount_borrowed'],y['loan_last'])
        if(check ==  False):
          pay_check = prediction_by_model(y['age'],y['amount_borrowed'],y['light_expense'],y['marital_status'],y['occupation_status'],y['working_with_employ'],y['residential_status'],y['living_with_address'],y['kids'],y['loan_purpose'])
          if(pay_check==True):
              application_status = "Approved"
              message = MIMEText('<img src="https://drive.google.com/drive/u/0/folders/10ONKl2Tc_eChKsUQJICiMzx9M-nh6NHK"><br><h2><a href="https://moniready.aidaform.com/moniready-upload-form">Click Here For Further Procedure</a></h2>','html')
              message['to']=y['email']
              message['from'] = "monireadyinfo@gmail.com"
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
              application_status = "Rejected"
              message = MIMEText('<img src="https://drive.google.com/drive/u/0/folders/10ONKl2Tc_eChKsUQJICiMzx9M-nh6NHK"><br><h2><a href="https://moniready.aidaform.com/moniready-upload-form">Click Here For Further Procedure</a></h2>','html')
              message['to']=y['email']
              message['from'] = "monireadyinfo@gmail.com"
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
            application_status = "Rejected"
            message = MIMEText('<img src="https://drive.google.com/drive/u/0/folders/10ONKl2Tc_eChKsUQJICiMzx9M-nh6NHK">','html')
            message['to']=y['email']
            message['from'] = "monireadyinfo@gmail.com"
            message['subject']="Moniready Application"
            raw = base64.urlsafe_b64encode(message.as_bytes())
            raw = raw.decode()
            body={'raw':raw}
            try:
                res = (service.users().messages().send(userId="me",body=body).execute())
                print("your message has been sent")
            except:
                print("an error occured")
    params = []
    social_apps=""
    if('social_apps_Instagram' in user_dict.keys()):
      social_apps = social_apps + user_dict['social_apps_Instagram']+","
      del user_dict['social_apps_Instagram']
    if('social_apps_Facebook' in user_dict.keys()):
      social_apps = social_apps + user_dict['social_apps_Facebook']+","
      del user_dict['social_apps_Facebook']
    if('social_apps_Twitter' in user_dict.keys()):
      social_apps = social_apps + user_dict['social_apps_Twitter']+","
      del user_dict['social_apps_Twitter']
    if('social_apps_Snapchat' in user_dict.keys()):
      social_apps = social_apps + user_dict['social_apps_Snapchat']+","
      del user_dict['social_apps_Snapchat']
    if('social_apps_TikTok' in user_dict.keys()):
      social_apps = social_apps + user_dict['social_apps_TikTok']+","
      del user_dict['social_apps_TikTok']
    if('social_apps_Others' in user_dict.keys()):
      social_apps = social_apps + user_dict['social_apps_Others']+","
      del user_dict['social_apps_Others']

    user_dict['submission_date'] = str(date.today())
    user_dict['social_apps'] = social_apps
    user_dict['application_status'] = application_status

    for x in user_dict.values():
      params.append(x)
    
    data_ = [params]

    try:
      res = sheet_service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,range="Sheet1",valueInputOption="USER_ENTERED",body={"values":data_},insertDataOption='INSERT_ROWS').execute()
      print(res)
    except Exception as e:
      print(e)

    return render_template('end.html')
  


if __name__ == '__main__':
  app.run(port = int(os.environ.get("PORT", 5000)))


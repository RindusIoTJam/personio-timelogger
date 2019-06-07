#!/usr/bin/python3

from config_sample import *
from config import *
import sys
import os
import json
import re
from random import randint
from datetime import timedelta

SLACK_URL = 'http://4091d574.ngrok.io'

if len(sys.argv) == 1 or sys.argv[1] == '--help':
	help_message = 'Error. No argument' + '\n\n'
	help_message += 'Usage: att.py [date]' + '\n'
	help_message += 'Note: Date format yyyy/mm/dd' + '\n'
	print(help_message)
	exit()

def checkDate (dateInput):
	return re.fullmatch(r"\A([\d]{4})-([\d]{2})-([\d]{2})", dateInput)

if (not(checkDate(sys.argv[1]))):
	error_message = 'Error. Wrong date format' + '\n\n'
	error_message += 'Usage: att.py [date]' + '\n'
	error_message += 'Note: Date format yyyy/mm/dd' + '\n'
	print(error_message)
	exit()

WORKING_TIME = WORKING_HOURS * 60
MIN_START_TIME = STARTING_HOUR * 60
COOKIE = 'cookie.txt'
LOGIN_URL = 'https://rindus.personio.de/login/index';
ATTENDANCE_URL = 'https://rindus.personio.de/api/v1/employees/' + PROFILE_ID+ '/attendances';


def clearCookie():
	with open(COOKIE, "w"):
		pass

def doGet(url):
	command = ('curl ' + url +
		' --insecure' + 
		' --location' +
		' --cookie ' + COOKIE +
		' --cookie-jar ' + COOKIE +
		' >/dev/null 2>&1'
	)
	os.system(command)
	return

def doPost(url, data):
	command = ('curl ' + url +
		# ' -X POST' +
		' --insecure' + 
		' --location' +
		' --cookie ' + COOKIE +
		' --cookie-jar ' + COOKIE +
		' --data "' + data + '"' +
		' >/dev/null 2>&1'
	)
	os.system(command)
	return


def doPostJSON(url, data):
	json_data = json.dumps(data)
	command = ('curl ' + url +
		' -X POST' +
		' --header "Content-Type: application/json"' +
		' --header "Content-Length: ' + str(len(json_data)) + '"' +
		' --insecure' + 
		' --cookie ' + COOKIE +
		' --cookie-jar ' + COOKIE +
		' --data \'' + json_data + '\''
	)
	os.system(command)
	return

def generateAttendance(date):
	post_date = date + 'T00:00:00+02:00'
	break_time = randint(50, 70)
	start_time = MIN_START_TIME + randint(5,45)
	working_time = randint(WORKING_TIME - 25, WORKING_TIME - 5)
	end_time = start_time + working_time

	return [{
		'id': None,
		'date': post_date,
		'start_time': start_time,
		'break_time': break_time,
		'end_time': end_time,
		'comment': ''
	}]

def objectToURLParams(obj):
	output = ''
	for name, value in obj.items():
		output = output + name + '=' + value + '&'

	return output

def slack_bang(data):
	postData = {
		'email': EMAIL,
		'slackSecret': SLACK_SECRET,
		'day': str(data[0]['date'])[0:10],
		'startTime': str(timedelta(minutes=data[0]['start_time'])),
		'endTime': str(timedelta(minutes=data[0]['end_time'])),
		'breakTime': str(data[0]['break_time'])
	}

	json_data = json.dumps(postData)

	
	command = "curl --silent -X POST -H 'Content-type: application/json'"
	command += " --data '" +json_data + "'"
	command += " http://4091d574.ngrok.io/timelogger"
	command += " > /dev/null"
	#print(command)
	os.system(command)

# RUN
clearCookie()
doGet(LOGIN_URL)
login_data = 'email=' + EMAIL + '&password=' + PASSWORD
doPost(LOGIN_URL, login_data)

attendance_entry = generateAttendance(sys.argv[1])
#print(attendance_data)
doPostJSON(ATTENDANCE_URL, attendance_entry)
slack_bang(attendance_entry)
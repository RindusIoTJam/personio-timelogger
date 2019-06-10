#!/usr/bin/env python3

import sys
import os
import json
import re
import urllib.request as request
import urllib.parse as parse
import http.cookiejar

from random import randint
from datetime import timedelta

from config_sample import *
try:
	from config import *
except ImportError:
	print('WARNING: no config.py found. Please RTFM!')
	sys.exit(1)

if len(sys.argv) == 1 or sys.argv[1] == '--help':
	help_message = 'Error. No argument' + '\n\n'
	help_message += 'Usage: att.py [date]' + '\n'
	help_message += 'Note: Date format yyyy/mm/dd' + '\n'
	print(help_message)
	exit()


def checkDate(dateInput):
	return re.fullmatch(r"\A([\d]{4})-([\d]{2})-([\d]{2})", dateInput)


if not checkDate(sys.argv[1]):
	error_message = 'Error. Wrong date format' + '\n\n'
	error_message += 'Usage: att.py [date]' + '\n'
	error_message += 'Note: Date format yyyy/mm/dd' + '\n'
	print(error_message)
	exit()

WORKING_TIME = WORKING_HOURS * 60
MIN_START_TIME = STARTING_HOUR * 60
COOKIE = 'cookie.txt'
LOGIN_URL = 'https://rindus.personio.de/login/index'
ATTENDANCE_URL = 'https://rindus.personio.de/api/v1/employees/' + PROFILE_ID + '/attendances'


def generateAttendance(date):
	post_date = date + 'T00:00:00+02:00'
	break_time = randint(50, 70)
	start_time = MIN_START_TIME + randint(5,45)
	working_time = randint(WORKING_TIME - 25, WORKING_TIME - 5)
	end_time = start_time + working_time

	return [{
		'email': EMAIL,
		'id': None,
		'date': post_date,
		'start_time': start_time,
		'break_time': break_time,
		'end_time': end_time,
		'comment': ''
	}]


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
	command += " --data '" + json_data + "'"
	command += " " + SLACK_BOT_URL + "/timelogger"
	command += " > /dev/null"
	# print(command)
	os.system(command)


if __name__ == "__main__":
	# RUN

	cookieJar = http.cookiejar.CookieJar()
	cookiePro = request.HTTPCookieProcessor(cookieJar)
	urlOpener = request.build_opener(cookiePro)

	# Login
	login_data = {
		'email':    EMAIL,
		'password': PASSWORD
	}
	data = parse.urlencode(login_data).encode()
	urlOpener.open(LOGIN_URL, data=data)

	# Add attendance
	attendance_entry = generateAttendance(sys.argv[1])
	urlOpener.addheaders = [('Content-Type', 'application/json')]
	urlOpener.open(ATTENDANCE_URL, data=bytes(json.dumps(attendance_entry), 'utf-8'))

	# Inform User
	slack_bang(attendance_entry)

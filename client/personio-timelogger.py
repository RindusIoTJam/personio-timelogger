#!/usr/bin/env python3

import json
import os
import re
import sys
import uuid
import functools
from datetime import datetime, timedelta
from random import randint

import requests

try:
    from config import (
        ABSENCES_URL,
        ATTENDANCE_URL,
        BREAK_HOUR,
        BREAK_TIME_MINUTES,
        EMAIL,
        HOLIDAYS_URL,
        LOGIN_URL,
        PASSWORD,
        PROFILE_ID,
        SLACK_BOT_URL,
        SLACK_MESSAGE,
        SLACK_SECRET,
        STARTING_HOUR,
        WORKING_HOURS,
    )

except ImportError:
    print("WARNING: no config.py found. Please RTFM!")
    exit()


def check_date(dateInput):
    return re.fullmatch(r"\A([\d]{4})-([\d]{2})-([\d]{2})", dateInput)


def generate_attendance(
    date, starting_hour, break_hour, working_hours, break_time_minutes, employee_id
):
    start_time = datetime.strptime(f"{date} {starting_hour}", "%Y-%m-%d %H:%M")
    break_time = datetime.strptime(f"{date} {break_hour}", "%Y-%m-%d %H:%M")
    working_time = (working_hours + 1) * 60
    working_time = randint(working_time - 25, working_time - 5)

    start_time += timedelta(minutes=randint(5, 45))
    break_time += timedelta(minutes=randint(0, 30))

    lunch_time = break_time_minutes + randint(0, 15)

    start_time_second = break_time + timedelta(minutes=lunch_time)
    working_time_second = int(
        working_time - (start_time_second - start_time).total_seconds() / 60
    )
    end_time = start_time_second + timedelta(minutes=working_time_second)

    return [
        {
            "id": str(uuid.uuid1()),
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": break_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "comment": "",
            "project_id": None,
            "employee_id": employee_id,
            "activity_id": None,
        },
        {
            "id": str(uuid.uuid1()),
            "start": start_time_second.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "comment": "",
            "project_id": None,
            "employee_id": employee_id,
            "activity_id": None,
        },
    ]


def slack_bang(attendance_date, message):
    postData = {
        "email": EMAIL,
        "slackSecret": SLACK_SECRET,
        "day": attendance_date,
        "startTime": "",
        "endTime": "",
        "breakTime": "",
        "message": message,
    }

    json_data = json.dumps(postData)

    command = "curl --silent -X POST -H 'Content-type: application/json'"
    command += " --data '" + json_data + "'"
    command += " " + SLACK_BOT_URL + "/timelogger"
    command += " > /dev/null"
    # print(command)
    os.system(command)


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "--help" or not check_date(sys.argv[1]):
        print(
            f"""
            Error. No argument or wrong date format\n\n
            Usage: {__file__} [date]\n
            Note: Date format yyyy-mm-dd \n
            """
        )
        exit()

    attendance_date = sys.argv[1]

    # Create request session
    session = requests.Session()

    # Login into Personio
    response = session.post(
        LOGIN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"email": EMAIL, "password": PASSWORD},
    )

    # Check Working Day
    response = session.get(
        f'{HOLIDAYS_URL}&start_date={attendance_date}&end_date={attendance_date}'
    )
    isHoliday = len(json.loads(response.text)['data'])

    # Check User Abscense
    response = session.get(
        f'{ABSENCES_URL}/{PROFILE_ID}/absences/types'
    )
    absenceTypes = ','.join(list(map(lambda a : str(a['id']), json.loads(response.text)['data'])))
    response = session.get(
        f'{ABSENCES_URL}/{PROFILE_ID}/absences/periods?filter[startDate]={attendance_date}&filter[endDate]={attendance_date}&filter[absenceTypes]={absenceTypes}'
    )
    isAbsence = len(json.loads(response.text)['data'])

    if isHoliday or isAbsence:
        message = 'Not working day'
        if SLACK_MESSAGE:
            # Inform User
            slack_bang(attendance_date, message)
        else:
            print(message)
        exit()

    # Log the attendance
    response = session.post(
        ATTENDANCE_URL,
        json=generate_attendance(
            sys.argv[1],
            STARTING_HOUR,
            BREAK_HOUR,
            WORKING_HOURS,
            BREAK_TIME_MINUTES,
            PROFILE_ID,
        ),
    )

    data = json.loads(response.text)
    try:
        message = f"Error: {attendance_date} - {data['error']['message']}"
    except KeyError:
        message = f"Success: attendance on {attendance_date} registered!"

    if SLACK_MESSAGE:
        # Inform User
        slack_bang(attendance_date, message)
    else:
        print(message)

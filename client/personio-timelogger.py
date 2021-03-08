#!/usr/bin/env python3

import datetime
import sys
import os
import json
import re
import pytz
import requests
import uuid

from time import sleep
from random import randint
from datetime import datetime, timedelta

try:
    from config_sample import (
        ATTENDANCE_URL,
        BREAK_HOUR,
        BREAK_TIME_MINUTES,
        EMAIL,
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
    sys.exit(1)


def check_date(dateInput):
    return re.fullmatch(r"\A([\d]{4})-([\d]{2})-([\d]{2})", dateInput)


def format_datetime(time_to):
    return f"{date}T{time}Z"


def generate_attendance(date, starting_hour, break_hour, working_hours, break_time_minutes, employee_id):
    start_time = datetime.strptime(f"{date} {starting_hour}", '%Y-%m-%d %H:%M')
    break_time = datetime.strptime(f"{date} {break_hour}", '%Y-%m-%d %H:%M')
    working_time = working_hours * 60
    working_time = randint(working_time - 25, working_time - 5)

    start_time += timedelta(minutes=randint(5, 45))
    break_time += timedelta(minutes=randint(0, 30))

    lunch_time = break_time_minutes + randint(0, 15)

    start_time_second = break_time + timedelta(minutes=lunch_time)
    working_time_second = int(working_time - (start_time_second - start_time).total_seconds() / 60)
    end_time = start_time_second + timedelta(minutes=working_time_second + randint(0,30))

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


def slack_bang(data):
    postData = {
        "email": EMAIL,
        "slackSecret": SLACK_SECRET,
        "day": str(data[0]["date"])[0:10],
        "startTime": str(timedelta(minutes=data[0]["start_time"]))
        if (data[0].get("start_time") is not None)
        else "",
        "endTime": str(timedelta(minutes=data[0]["end_time"]))
        if (data[0].get("end_time") is not None)
        else "",
        "breakTime": str(data[0]["break_time"])
        if (data[0].get("break_time") is not None)
        else "",
        "message": str(data[0]["message"])
        if (data[0].get("message") is not None)
        else "",
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

    # Wait between 1-10 seconds before logging in
    # sleep(randint(1, 10))

    # Create request session
    session = requests.Session()

    # Login into Personio
    response = session.post(
        LOGIN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"email": EMAIL, "password": PASSWORD},
    )

    # Log the attendance
    response = session.post(
        ATTENDANCE_URL,
        json=generate_attendance(
            sys.argv[1], STARTING_HOUR, BREAK_HOUR, WORKING_HOURS, BREAK_TIME_MINUTES, PROFILE_ID
        ),
    )

    data = json.loads(response.text)
    try:
        message = f"Error: {attendance_date} - {data['error']['message']}"
    except KeyError:
        message = f"Success: attendance on {attendance_date} registered!"

    if SLACK_MESSAGE:
        # Inform User
        slack_bang(message)
    else:
        print(message)

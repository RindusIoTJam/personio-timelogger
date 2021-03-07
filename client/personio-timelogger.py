#!/usr/bin/env python3

import sys
import os
import json
import re
import pytz
import requests
import uuid

from time import sleep
from random import randint
from datetime import timedelta
from datetime import datetime

try:
    from config_sample import (
        ATTENDANCE_URL,
        BREAK_HOUR,
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


def format_datetime(date, time):
    return f"{date}T{time}Z"


def generate_attendance(date, starting_hour, break_hour, working_hours, employee_id):
    min_start_time = starting_hour * 60
    working_time = working_hours * 60
    break_time = break_hour * 60

    # randint(50, 70)

    start_time = min_start_time + randint(5, 45)
    working_time = randint(working_time - 25, working_time - 5)
    end_time = start_time + working_time

    return [
        {
            "id": str(uuid.uuid1()),
            "start": format_datetime(date, start_time),
            "end": format_datetime(date, end_time),
            "comment": "",
            "project_id": None,
            "employee_id": employee_id,
            "activity_id": None,
        },
        {
            "id": str(uuid.uuid1()),
            "start": format_datetime(date, start_time),
            "end": format_datetime(date, end_time),
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
    sleep(randint(1, 10))

    print(generate_attendance(
        sys.argv[1], STARTING_HOUR, BREAK_HOUR, WORKING_HOURS, PROFILE_ID
    ))

    # # Create request session
    # session = requests.Session()

    # # Login into Personio
    # response = session.post(
    #     LOGIN_URL,
    #     headers={"Content-Type": "application/x-www-form-urlencoded"},
    #     data={"email": EMAIL, "password": PASSWORD},
    # )

    # # Log the attendance
    # response = session.post(
    #     ATTENDANCE_URL,
    #     json=generate_attendance(
    #         sys.argv[1], STARTING_HOUR, BREAK_HOUR, WORKING_HOURS, PROFILE_ID
    #     ),
    # )

    # data = json.loads(response.text)
    # try:
    #     message = f"Error: {attendance_date} - {data['error']['message']}"
    # except KeyError:
    #     message = f"Success: attendance on {attendance_date} registered!"

    # Inform User
    # slack_bang(message)

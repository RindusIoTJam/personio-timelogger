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

    command = (
        f"curl --silent -X POST -H 'Content-type: application/json'"
        f" --data '{json_data}'"
        f" {SLACK_BOT_URL}/timelogger"
        f" > /dev/null"
    )
    os.system(command)


def inform_user(attendance_date, message, slack_message):
    if slack_message:
        slack_bang(attendance_date, message)
    else:
        print(message)


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "--help":
        print(f"Error: No argument / Usage: {__file__} [date]")
        exit()

    try:
        locals().update(json.loads(sys.argv[1]))
        sys.argv[1] = DAY
    except ValueError:
        pass

    if not check_date(sys.argv[1]):
        print(f"ERROR: Wrong date format / Expected format yyyy-mm-dd")
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
        f"{HOLIDAYS_URL}"
        f"&start_date={attendance_date}"
        f"&end_date={attendance_date}"
    )
    isHoliday = len(json.loads(response.text)["data"])

    # Check User Abscense
    response = session.get(f"{ABSENCES_URL}/{PROFILE_ID}/absences/types")
    absenceTypes = ",".join(
        list(map(lambda a: str(a["id"]), json.loads(response.text)["data"]))
    )

    response = session.get(
        f"{ABSENCES_URL}/{PROFILE_ID}/absences/"
        f"periods?filter[startDate]={attendance_date}"
        f"&filter[endDate]={attendance_date}"
        f"&filter[absenceTypes]={absenceTypes}"
    )
    isAbsence = len(json.loads(response.text)["data"])

    if isHoliday or isAbsence:
        inform_user(attendance_date, "Not working day", SLACK_MESSAGE)
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

    inform_user(attendance_date, message, SLACK_MESSAGE)

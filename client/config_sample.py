# Personio credentials
EMAIL = 'name.surname@rindus.de'
PASSWORD = r'myStrong!Password'
PROFILE_ID = '0000000' # This can be found in your personio profile URL

# Slack credentials
SLACK_MESSAGE = False
SLACK_SECRET = 'aaaaaaa'
SLACK_BOT_URL = 'URL-TO-BOT'

# App configuration
STARTING_HOUR = "08:00"  # Hour you usually start working in the morning
BREAK_HOUR = "13:00"  # Hour you usually take your lunch break
WORKING_HOURS = 8
BREAK_TIME_MINUTES = 30

# Personio Configuration
LOGIN_URL = "https://rindus.personio.de/login/index"
ATTENDANCE_URL = f'https://rindus.personio.de/api/v1/attendances/periods'
HOLIDAYS_URL = f'https://rindus.personio.de/api/v1/holidays?holiday_calendar_ids[]=977'
ABSENCES_URL = f'https://rindus.personio.de/api/v1/employees/'

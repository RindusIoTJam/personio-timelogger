const dateFormat = 'yyyy-LL-dd';

const defaultConfiguration = {
    slackSecret: null,
    final: null,
    mode: 'day',
    startingHour: '08:00',
    breakHour: '13:00',
    breakTime: 30,
    workingHours: 8,
};

const requiredParameters = [
    {
        name: 'email',
        description: 'your rindus email'
    },
    {
        name: 'password',
        description: 'your personio password'
    },
    {
        name: 'profileId',
        description: 'your personio profileId'
    }
];

const optionalParameters = [
    {
        name: 'mode',
        description: 'Single day or Range. Options: day | range',
        default: defaultConfiguration['mode']
    },
    {
        name: 'day',
        description: 'The day to log the time. Initial day if Range mode is set',
        default: 'the day you make the request'
    },
    {
        name: 'final',
        description: 'The final day to log the time. Only in Range mode. The final day is included in the range.',
        default: defaultConfiguration['final']
    },
    {
        name: 'startingHour',
        description: 'The hour you start working. Decimal values allowed',
        default: defaultConfiguration['startingHour']
    },
    {
        name: 'breakHour',
        description: 'Hour you usually take your lunch break',
        default: defaultConfiguration['breakHour']
    },
    {
        name: 'breakTime',
        description: 'Length (in minutes) of your lunch time.',
        default: defaultConfiguration['breakTime']
    },
    {
        name: 'workingHours',
        description: 'Legal working hours, excluding break.',
        default: defaultConfiguration['workingHours']
    },
    {
        name: 'slackSecret',
        description: 'Secret provided by Slack for notifications. More info <a href="#slackbot">below</a>',
        default: defaultConfiguration['slackSecret']
    }
];

const requestExamples = [
    {
        title: 'Log today with default options',
        path: '?email=YOUR_EMAIL&password=YOUR_PASSWORD'
    },
    {
        title: 'Log a single day with full configuration',
        path: '?email=YOUR_EMAIL&password=YOUR_PASSWORD&slackSecret=YOUR_SLACK_SECRET&day=2021-03-15&startingHour=09:00&breakHour=14:00&breakTime=50&workingHours=8'
    },
    {
        title: 'Log days in a date range',
        path: '?email=YOUR_EMAIL&password=YOUR_PASSWORD&day=2021-03-15&final=2021-03-20'
    },

]

module.exports = {
    dateFormat,
    defaultConfiguration,
    requiredParameters,
    optionalParameters,
    requestExamples,
};

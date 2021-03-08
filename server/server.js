// https://tutorials.botsfloor.com/building-a-node-js-slack-bot-before-your-microwave-popcorn-is-ready-8946651a5071

require('dotenv').config();
const { exec } = require("child_process");
const express = require('express');
const bodyParser = require('body-parser');
const request = require("request");
var async = require("async");
const { DateTime } = require("luxon");
const sleep = require('sleep');

const { validateDateString, validateTimeString, getDateFromString } = require('./helper');

const constants = require('./constants');
const { addUser, checkSecret } = require('./dbhandler');
const { exit } = require('process');

const app = express();
const port = process.env.PORT || 3000;
app.listen(port, function() {
  console.log('TimeLogger Bot is listening on port ' + port);
});

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

app.post('/register', async (req, res) => {
	const userId = req.body.user_id;
	const channelId = req.body.channel_id;

	const secret = async () => {
		return addUser(userId);
	};

	const userSecret = await secret();

	var data = {
		form: {
			token: process.env.SLACK_AUTH_TOKEN,
			channel: channelId,
			user: userId,
			text: "Your secret is " + userSecret
	}};

	request.post('https://slack.com/api/chat.postEphemeral', data, function (error, response, body) {
		res.json();
	});
});

app.post('/timelogger', async (req, res) => {
	const { email, slackSecret, day, startTime, endTime, breakTime, message } = req.body;

	const data = {
		form: {
			token: process.env.SLACK_AUTH_TOKEN,
			email
		}
	}

	request.post('https://slack.com/api/users.lookupByEmail', data, async (error, response, body) => {
		const userId = JSON.parse(body).user.id;

		const validUser = await checkSecret(userId, slackSecret);

		if (validUser) {
				const text = message
					? `Day: ${day}\nMessage: ${message}\n`
					: `Day: ${day}\nStart time: ${startTime}\nEnd time: ${endTime}\nBreak: ${breakTime}\n`

				const data = {
					form: {
						token: process.env.SLACK_AUTH_TOKEN,
						channel: `${userId}`,
						text
					}
				};

				request.post('https://slack.com/api/chat.postMessage', data, function (error, response, body) {
					res.json();
				});
		} else {
			res.json({ "error": "Invalid secret" });
		}
	});
});

// Web Tool
app.get('/log', async (req, res) => {
	// Help page
	const fullUrl = req.protocol + '://' + req.get('host') + req.originalUrl;
	if (Object.keys(req.query).length === 0) {

		return res.send(`
			<style>
				table {
					font-family: arial, sans-serif;
					border-collapse: collapse;
					width: 100%;
				}

				td, th {
					border: 1px solid #ddd;
					text-align: left;
					padding: 8px;
				}
				td:first-child {
					font-weight: bold;
				}
				th {
					background-color: #eee;
				}

				pre {
					display: inline-block;
					border: 1px solid #ccc;
					background-color: #eee;
					padding: 5px;
					border-radius: 5px;
				}
			</style>
			<h1>Personio Timelogger 2</h1>
			<p>Welcome to the Personio Timelogger web tool.</p>
			<p>You will be able to log yout working time in Personio system.</p>
			<h3>Required parameters:</h3>
			<table>
				<tr><th>Name</th><th>Description</th></tr>
				${constants.requiredParameters.map(param => `<tr><td>${param.name}</td><td>${param.description}</td></tr>`).join('')}				
			</table>
			<h3>Optional parameters:</h3>
			<table>
				<tr><th>Name</th><th>Description</th><th>Default value</th></tr>
				${constants.optionalParameters.map(param => `<tr><td>${param.name}</td><td>${param.description}</td><td>${param.default}</td></tr>`).join('')}
			</table>
			<h3>Examples</h3>
			${constants.requestExamples.map(example => `<dt>${example.title}</dt><dd><pre>${fullUrl}${example.path}</pre></dd>`).join('')}
			<h3>More Information</h3>
			<a name="slackbot"></a>
			<h4>The SlackBot</h4>
			<p>The bot will personally send you feedback when a new post to personio has been successfully done. You need to register into the bot to be able to receive incoming messages from it. Follow the following instructions:</p>
			<ol>
				<li>Open Rindus Slack</li>
				<li>Go to the bottom of the left navbar and add the app TimeLogger</li>
				<li>In the conversation with the app, run <pre>/timelogger</pre></li>
			</ol>
			<p>You will receive a secret key from the bot. This secret key is the value of the <strong>slackSecret</strong> parameter</p>
		`);
	}

	// Generate configuration
	const config = {
		day: DateTime.now().toFormat(constants.dateFormat),
		...constants.defaultConfiguration,
		...req.query
	};

	// Check input data
	const missingArguments = [];
	if (!config.email) missingArguments.push('email');
	if (!config.password) missingArguments.push('password');
	if (!config.profileId) missingArguments.push('profileId');

	if (missingArguments.length) {
		res.send(`
			<h1>Error</h1>
			<p>The request requires the following arguments:</p>
			<ul>${missingArguments.map(arg => `<li>${arg}</li>`).join('')}</ul>
			<p>Visit <a href="/log">Home</a> for help.</p>
		`);
	}

	const wrongArguments = [];
	console.log(config.startingHour);
	if (!validateDateString(config.day)) wrongArguments.push('day');
	if (config.final && !validateDateString(config.final)) wrongArguments.push('final');
	if (!validateTimeString(config.startingHour)) wrongArguments.push('startingHour');
	if (isNaN(config.workingHours)) wrongArguments.push('workingHours');
	if (!validateTimeString(config.breakHour)) wrongArguments.push('breakHour');
	if (isNaN(config.breakTime)) wrongArguments.push('breakTime');

	if (wrongArguments.length) {
		res.send(`
			<h1>Error</h1>
			<p>Uncompatible types in the following arguments:</p>
			<ul>${wrongArguments.map(arg => `<li>${arg}</li>`).join('')}</ul>
			<p>Visit <a href="/log">Home</a> for help.</p>
		`);
	}

	// Generate Config JSON
	const pythonConfig = {
		DAY: config.day,

		EMAIL: 'borja.espildora@rindus.de',
		PASSWORD: 'vuiChi7u!1',
		PROFILE_ID: '177706',

		STARTING_HOUR: config.startingHour, //'08:00',  // Hour you usually start working in the morning
		BREAK_HOUR: config.breakHour, //'13:00', // Hour you usually take your lunch break
		WORKING_HOURS: config.workingHours, //8,
		BREAK_TIME_MINUTES: config.breakTime, //30,

		LOGIN_URL: 'https://rindus.personio.de/login/index',
		ATTENDANCE_URL: 'https://rindus.personio.de/api/v1/attendances/periods'
	};
	if (config.slackSecret) {
		pythonConfig['SLACK_MESSAGE'] = true;
		pythonConfig['SLACK_SECRET'] = config.slackSecret;
		pythonConfig['SLACK_BOT_URL'] = config.SLACK_BOT_URL;
	} else {
		pythonConfig['SLACK_MESSAGE'] = false;
	}

	const command = 'python3 ../client/personio-timelogger.py \'' + JSON.stringify(pythonConfig) + '\'';
	console.log(command);
	/*exec(command, (error, stdout, stderr) => {
		if (error) {
			console.log(`error: ${error.message}`);
			return;
		}
		if (stderr) {
			console.log(`stderr: ${stderr}`);
			return;
		}
		console.log(`stdout: ${stdout}`);
	});
	*/
	exit();

	

	// Run the logger
	/*
	const connection = await getConnection(config.email, config.password);
	switch (config.mode) {
		case 'range':
			const startDate = getDateFromString(config.day);
			const endDate = getDateFromString(config.final);

			let day;
			let currentDate = startDate;
			while (currentDate.toMillis() <= endDate.toMillis()) {
				day = currentDate.toFormat(dateFormat);
				await setAttendance(connection, {
					...config,
					day
				});
				currentDate = currentDate.plus({ day: 1 });
				sleep.sleep(1);
			}
			res.send('OK');
			break;
		default:
			await setAttendance(connection, config);
			res.send('OK');
			break;
	}
	return;
	*/
});	
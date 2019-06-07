// https://tutorials.botsfloor.com/building-a-node-js-slack-bot-before-your-microwave-popcorn-is-ready-8946651a5071

require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const request = require("request");
var async = require("async");

const { addUser, checkSecret } = require('./dbhandler')

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
			text: "Your secret is " + userSecret
	}};

	request.post('https://slack.com/api/chat.postMessage', data, function (error, response, body) {
		res.json();
	});
});

app.post('/timelogger', async (req, res) => {
	const { email, slackSecret, day, startTime, endTime, breakTime } = req.body;

	const data = {
		form: {
			token: process.env.SLACK_AUTH_TOKEN,
			email
		}
	}

	request.post('https://slack.com/api/users.lookupByEmail', data, async (error, response, body) => {
		var userId = JSON.parse(body).user.id;

		const validUser = await checkSecret(userId, slackSecret);

		if (validUser) {
			const data = {
				form: {
					token: process.env.SLACK_AUTH_TOKEN,
					user: `${userId}`,
				}
			};
			request.post('https://slack.com/api/im.open', data, function (error, response, body) {
				var channelId = JSON.parse(body).channel.id;
				
				const data = {
					form: {
						token: process.env.SLACK_AUTH_TOKEN,
						channel: `${channelId}`,
						as_user: false,
						text: `Day: ${day}\nStart time: ${startTime}\nEnd time: ${endTime}\nBreak: ${breakTime}\n`
					}
				};
				request.post('https://slack.com/api/chat.postMessage', data, function (error, response, body) {
					res.json();
				});
				
			});
		}
	});
})
// To create db and table, run on unix:
// sqlite3 users.db "create table users(user text PRIMARY KEY, secret text);"
const database = require('sqlite-async');
const shortid = require('shortid');
var async = require("async");


function generateSecret() {
	return shortid.generate();
}

module.exports = {

	addUser: async (userId) => {
		if (!userId) {
			return false;
		}

        let userSecret;

		userSecret = await database.open('./users.db', database.OPEN_READWRITE)
            .then(db => {
                const sql = `SELECT secret FROM users WHERE user = ? LIMIT 1`
                return db.get(sql, [userId])
                    .then(row => {
                        if (row) {
                            return row.secret;
                        }
                        return null;
                    })
                    .catch(err => {
                        console.log(1, err)
                        return false;
                    })
            });

        if (userSecret) {
            return userSecret;
        }

		const newSecret = generateSecret();
        userSecret = await database.open('./users.db', database.OPEN_READWRITE)
        .then(db => {
            const sql = `INSERT INTO users(user, secret) VALUES (?, ?)`
            return db.run(sql, [userId, newSecret])
                .then(row => {
                    db.close();
                    return newSecret;
                })
                .catch(err => {
                    console.log(2, err)
                    return false;
                })
        });

        return userSecret;
	},

	checkSecret: async (userId, secret) => {
        if (!userId) {
            return false;
        }

        const match = await database.open('./users.db', database.OPEN_READWRITE)
            .then(db => {
                const sql = `SELECT secret FROM users WHERE user = ? LIMIT 1`
                return db.get(sql, [userId])
                    .then(row => {
                        if (row) {
                            return row.secret === secret;
                        }
                        return false;
                    })
                    .catch(err => {
                        console.log(1, err)
                        return false;
                    })
            });

        return match;
        /*
		if (!userId || !secret) {
			return false;
		}

		const db = new sqlite3.Database('./users.db', sqlite3.OPEN_READWRITE, (err) => {
			if (err) {
				return err.message;
			}
		});

		db.serialize(() => {
			db.each(`SELECT * FROM users WHERE user LIKE ${userId}`, (err, row) => {
				if (err){
					return false;
				}
				return row.secret === secret;
			});
		});
		db.close();

		return 'hola';
        */
	},

	getSecret: function(userId) {
		if (!userId) {
			return false;
		}

		const db = new sqlite3.Database('./users.db', sqlite3.OPEN_READWRITE, (err) => {
			if (err) {
				return err.message;
			}
		});

		db.serialize(() => {
			db.each(`SELECT * FROM users WHERE user LIKE ${userId}`, (err, row) => {
				if (err){
					return false;
				}
				return row.secret;
			});
		});
		db.close();
	}
};
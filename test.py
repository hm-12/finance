import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd


db = SQL("sqlite:///finance.db")

# rows = db.execute("SELECT *FROM users")

# for row in rows:
#     print(row)

# print(type(rows))
# print(rows[0]['username'])
# print(rows[1]['username'])
# s = rows[0]['username']
# if "hossein" == s:
#     print('identical')

# rows = db.execute("SELECT * FROM users WHERE username = :username",
#                           username="ed")
# # Ensure username DOSE NOT exist
# if len(rows) != 1:
#     print("not exist")
# else:
#     print(" exist")
#     print(len(rows))

# rows = db.execute("INSERT INTO users(username, hash) VALUES(:username, :pass_hash)", username="deneme_username5", pass_hash="deneme_hash2")

# # print(len(rows))
# print(rows)

# quote = "tu".upper()

# rows = db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=555, id=3)

# rows = db.execute("SELECT cash FROM users WHERE id = :id", id=3)

# rows = db.execute("SELECT *FROM users")
# print(rows)

# print(db.execute("SELECT cash FROM users WHERE id = :id", id=3)[0]["cash"])

# histories = db.execute("SELECT *FROM account_activities WHERE id = :id", id=14)

# print(histories)
# print(type(histories))
# i = 0
# print(histories[0]["price"])
# print(histories[1]["price"])
# print(histories[2]["price"])

# rows = db.execute("SELECT symbol FROM account_activities  GROUP BY symbol")
# rows1 = db.execute("SELECT symbol, SUM(shares) FROM account_activities GROUP BY symbol HAVING shares > 0")
# rows = db.execute("SELECT SUM(shares) FROM account_activities GROUP BY :symbol ", symbol="u") #26 total
# rows = db.execute("SELECT  SUM(shares) FROM account_activities WHERE symbol = :symbol GROUP BY symbol", symbol="NFLX") #OK


# rows1 = db.execute("SELECT symbol, SUM(shares) as total_shares FROM account_activities GROUP BY symbol HAVING total_shares > 0")


# for symbol in rows1:
#     print(symbol["symbol"])
#     print("")

# stocks = db.execute("SELECT symbol, price, SUM(shares) as total FROM account_activities WHERE id = :id GROUP BY symbol HAVING total > 0",
#             id=14)

# print(stocks)

# user_total_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=14)
# print(user_total_cash[0]['cash'])

# print(quote)

# stocks = db.execute("SELECT symbol, price, SUM(shares) as total FROM account_activities WHERE id = :id GROUP BY symbol HAVING total > 0",
#             id=14)
# symbol = []
# for s in stocks:
#     symbol = lookup("f")

# stocks = db.execute("SELECT symbol, SUM(shares) as total FROM account_activities WHERE id = :id  GROUP BY symbol HAVING total > 0", id=14)

# print(stocks)
# print(stocks[0].get("total"))

# print(type(stocks))

stocks = db.execute("SELECT SUM(shares) as total FROM account_activities WHERE id = :id AND symbol = :symbol GROUP BY symbol",
            id=14, symbol="h")[0]['total']
shares = 4
r = db.execute("INSERT INTO account_activities(id,symbol,price,shares) VALUES (:id,:symbol,:price,:shares)", id=14, symbol="deneme", price=12, shares=-shares)
# stocks = db.execute("SELECT SUM(shares) as total FROM account_activities WHERE id = :id AND symbol = :symbol GROUP BY symbol",id=14, symbol="h")[0]["total"]


print(r)

# print(stocks + 3)
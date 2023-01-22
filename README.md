# MyBank

***
MyBank is bank application created by me where you can register, send and get money from other users, check your whole transaction history and more.

## Table of contents

***
* [Requirements](#Requirements)
* [About](#About)
* [Getting-started](#Getting-started):
    *  [Database](#Database)
    *  [env](#env)
* [Python](#Python): 
    * [app](#app)
    * [email](#email)
    * [email-send](#email-send)
    * [namec-heck](#name-check)
* [HTML](#HTML): 
    * [layout](#layout)
    * [apology](#apology)
    * [register](#register)
    * [login](#login)
    * [send-money](#send-money)
    * [history](#history)
    * [profile](#profile)
    * [settings](#settings)
* [Author](#Author)

## Requirements

***
Firstly you will need to create few things:
1.  [database](#Database)
2.  [env](#env)

## About

***
This application is bank where you register, create an account and send money to other users. When registerd application send email congratulating you on creating an account. Every person is presented with unique code, which you need to type if you want to send money (just like in real word). When you send money all transactions go to database and appears in /history. There you can filter data and find desired transaction. You can change your username, email or password in settings at any time. If any error occurs (for example you type password confirmation wrong) you are directed to /apology where you are told the reason of this error.

## Getting started

***

##### Database

You will need to create a SQL database, named "project.db", then in the database you will need to run this code:
```sql
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, code INTEGER NOT NULL UNIQUE, email TEXT NOT NULL, hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00);
CREATE UNIQUE INDEX username ON users (username);
CREATE TABLE transactions(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, receiver_id INTEGER NOT NULL, reason TEXT NOT NULL, money REAL NOT NULL, date DATETIME);
```

##### .env file

You will need to create .env file. There you will need to create a few variables:
```
MAIL_DEFAULT_SENDER = <Your email>
MAIL_PASSWORD = <Password of your email>
MAIL_USERNAME = <Username for your email>
```
Usually you will need to generate mail password using google because it prevents you from sending auto generated emails.

## Python

***
For frontend I used only python flask. The main program is `app.py`. To run it You will need to type 'flask run' in terminal.

##### App

1. I ensured that tempaltes are auto-reloaded, configured session to use filesystem (instead of signed cookies) and created databse variable named 'db'. After that I defined `apology` and made login required, ensured that responses are not cached:

2. Main route just renders `layout.html` tamplate.

3. **/register** gets inputs from `register.html` page, checks if they are not NULL. Then password is hashed and user is given a random number from 10000 to 99999
(it becomes his code). After that user is writen into database and auto-generated email is send to users presented email.

4. **/login** simply logs user in and redirects him to home page.

5. **/logout** just logs user out.

6. **/profile** just shows user data about him (username, code, email, cash).

7. **/settings** depending on which input is changed (username, email or password) changes it to prefered one. If user changes email auto-generated text congratulates him on his new email.

8. **/history** is main route that works with all data (transmitted and given). If you got moeny, 'Transfer amount' section becomes green, if not - red. The main problem is filtering. You have to check if input is not NULL and logical then filter using 'SQL'.

9. **/history/by-me** is the same as `/history` but uses only tarnsactions created by me.

10. **/history/to-me** is also the same as `/history` but uses only data where user is the one who got money.


##### Email

It consist of only one function which, if given user email, subject and text, sends that text to user.

##### Email-send

It is configuration for sending email. First program searches file to find `.env` file and gets email adress of a sender, his username, password. Then it checks if email is valid and then sends email.

##### Name-check

It consist of only one function that checks how much written and read usernames match. For that I use 'difflib' library.

## HTML

***
##### Layout

For layout I used `HTML` and template engine named `jinja`.

![Main](https://user-images.githubusercontent.com/90151740/213726689-e8a1d8cd-709d-423f-924c-5505da25bafc.png)

##### Apology

In `apology.html` I create text where user is told what is wrong.

##### Register

Here you need to write your prefered username, email adress and password.

![Register](https://user-images.githubusercontent.com/90151740/213726711-262e10cf-0d34-4b6e-aac1-7d5832a8cee5.png)

##### Login

Here you just need to write your username and password.

![Login](https://user-images.githubusercontent.com/90151740/213726680-6065c3ce-59df-471d-b4cf-5f70b4af048b.png)

##### Send-money

Here you need to write username of a person to whom you want to send money (you can make a few mistakes in his name because `name_check.py` checks if you made any ant lets it slide if it is not too much). Then you need to write receiver code, sum of money and reason.

![SendMoney](https://user-images.githubusercontent.com/90151740/213726716-1ecfb200-1e0f-4d6b-a3c9-79dbf6c28c24.png)

##### History

Here is presenter all of the transactions. Depending of your route (`/history`, `/history/by-me`, `history/to-me`) you are presented accordingly (all data, transactions where you send money, transactions where money is send to you). You can filter through data by username, reason, amount of cash, date. 

![History](https://user-images.githubusercontent.com/90151740/213726658-e6e6b050-2acd-4ce4-99bd-c0d1e83d1330.png)

##### Profile

Here you can see your current username, code,email, amount of cash. By pressing links you will be send to `/settings` route.

![Profile](https://user-images.githubusercontent.com/90151740/213726704-4256b640-67b6-4c96-b6ba-8b1b580113a1.png)

##### Settings

Here you can change your username, email, password.

![SettingsClosed](https://user-images.githubusercontent.com/90151740/213726725-10ce9dac-a4a4-4c7e-b5bf-5993cc26e172.png)
![SettingsOpened](https://user-images.githubusercontent.com/90151740/213726737-59475e3b-a432-42df-9609-5e207ee11fa1.png)

## Author

Feel free to contact me on [Linked In](https://www.linkedin.com/in/justinas-pranaitis-b0513325a/).
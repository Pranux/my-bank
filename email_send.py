from dotenv import dotenv_values
from email_validator import validate_email, EmailNotValidError
from email.message import EmailMessage
from flask_mail import Mail
from flask import render_template
import ssl
import smtplib

def apology(message):
    return render_template("apology.html", message=message)

def send_email(app, email, body):
    # Search for .env file
    config = dotenv_values(".env")

    # Email configuration
    MAIL_DEFAULT_SENDER = config["MAIL_DEFAULT_SENDER"]
    MAIL_PASSWORD = config["MAIL_PASSWORD"]
    MAIL_USERNAME = config["MAIL_USERNAME"]

    app.config["MAIL_DEFAULT_SENDER"] = MAIL_DEFAULT_SENDER
    app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = MAIL_USERNAME
    mail = Mail(app)

    #Checks if email is valid
    try:
        validation = validate_email(email)
        email = validation.email
    except EmailNotValidError:
        return apology("Email is invalid, check if you haven't made any mistake")

    #Sending email to user
    subject = "Hello"

    em = EmailMessage()
    em['From'] = MAIL_DEFAULT_SENDER
    em['To'] = email
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(MAIL_DEFAULT_SENDER, MAIL_PASSWORD)
        smtp.sendmail(MAIL_DEFAULT_SENDER, email, em.as_string())
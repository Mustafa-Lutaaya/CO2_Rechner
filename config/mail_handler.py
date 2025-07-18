import os # Accesses the environment variables.
import smtplib # Simple Mail Transfer Protocol to  send emails via an SMTP server
from email.mime.text import MIMEText # Creates email content in either plain text or HTML format.
from email.mime.multipart import MIMEMultipart # For Email that has multiple parts as both HTML & Attachments
from config.jwt_handler import JWTHandler # Imports JWT Handler Class 
from dotenv import load_dotenv # Loads secrets from .env.

load_dotenv() # Loads Environment Variables from .env File

# Email Credentials

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

base_url = os.getenv("base_url","http://127.0.0.1:5050")

class EmailHandler:
    @staticmethod
    def send_to_admin(name: str, email: str):  # Sends an email to the admin with JWT secure encoded links to approve or reject the user registration.

        # Generates JWT Tokens for approval or rejection actions
        approve_token = JWTHandler.create_token(email=email, action="approve", name=name)
        reject_token = JWTHandler.create_token(email=email, action="reject", name=name)

        # Constructs approval / rejection links
        approval_url = f"{base_url}/email/approve_user?token={approve_token}"
        rejection_url = f"{base_url}/email/reject_user?token={reject_token}"

        # HTML Content 4 The Email
        html_content = f"""
        <html>
        <body>
        <h2>New User Registration</h2>
        <h4>Name: {name}</h4> 
        <h4>Email: {email}</h4> 

        <h4>Please Choose an action:</h4>
        <a href="{approval_url}" style="padding:8px;background-color:green;color:white;text-decoration:none;"> Allow </a>
        &nbsp;
        <a href="{rejection_url}" style="padding:8px;background-color:red;color:white;text-decoration:none;"> Reject </a>
        </body>
        </html>
        """

        # Electronic Mail
        msg = MIMEMultipart("alternative")
        msg["From"] = SENDER_EMAIL
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = "New User Registration"
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Establishes connection to the SMTP server and send the email
                server.starttls() # Secures connetion
                server.login(SENDER_EMAIL, EMAIL_PASSWORD)
                server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, msg.as_string())
            print("Registration Email Sent")
        except Exception as e:
            print(f"Failed to send email: {e}")
            raise Exception("Error sending authentication email")
        
    @staticmethod
    def send_to_user(name: str, email: str, password: str):  # Sends an email to the User with a generated password

        # HTML Content 4 The Email
        html_content = f"""
        <html>
        <body>
        <h5>Welcome, {name}</h5>
        <p>Your registration has been approved</p>
        <p>Here are your login credentials</p>
        <ul>
        <li>Email: {email}</li>
        <li>Code: {password}</li>
        </ul>
        <p>
        <a href="https://co2-rechner.onrender.com/" style="padding:10px;background-color:blue;color:white;text-decoration:none;">
        Login Now</a>
        </p>
        </body>
        </html>
        """

        # Electronic Mail
        msg = MIMEMultipart("alternative")
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = "Account Approved"
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Establishes connection to the SMTP server and send the email
                server.starttls() # Secures connetion
                server.login(SENDER_EMAIL, EMAIL_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, msg.as_string())
            print("Credentials sent to user")
        except Exception as e:
            print(f"Failed to send email: {e}")
            raise Exception("Error sending credentials email")
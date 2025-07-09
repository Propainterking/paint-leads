import csv
import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

load_dotenv()

def write_csv(leads, filename="output/leads.csv"):
    os.makedirs("output", exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Name", "Address", "Phone", "Link", "Score"])
        for lead in leads:
            writer.writerow(lead)

def sync_to_google_sheets(leads):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Cox Paint Leads").sheet1
    sheet.clear()
    sheet.append_row(["Source", "Name", "Address", "Phone", "Link", "Score"])
    for lead in leads:
        sheet.append_row(lead)

def send_email(leads, filepath="output/leads.csv"):
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = sender
    msg["Subject"] = f"Cox’s Coatings Lead Report – {len(leads)} leads"

    body = "Your scrape is complete. Leads attached.\n\n— Copilot HQ 🎨"
    msg.attach(MIMEText(body, "plain"))

    with open(filepath, "rb") as f:
        msg.attach(MIMEApplication(f.read(), Name="leads.csv"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

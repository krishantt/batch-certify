from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import streamlit as st
import time

def put_text(image_path, text, position=(0,0), fontsize=100):
    image = Image.open(image_path)
    W, H = image.size
    font = ImageFont.truetype("Inter-SemiBold.ttf", fontsize)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox(position, text, font=font)
    draw.text(((W-w)/2, (H-h)/2), text, font=font, fill=(0,0,0))
    return image

def generate_batch(uploaded_image, x_cor, y_cor, font_size):
    data = st.session_state['data']

    for _, datae in data.iterrows():
        image = put_text(uploaded_image, datae.loc['name'], (x_cor, y_cor), font_size)
        image.save(f"./data/{datae.loc['name']}.pdf")

def send_mail(subject, body, bar):
    data = st.session_state['data']
    bar = st.progress(0, "Sending Mail")

    smtp_server = st.secrets["email-creds"]["smtp_server"]
    smtp_port = st.secrets["email-creds"]["smtp_port"]
    smtp_username = st.secrets["email-creds"]["smtp_username"]
    smtp_password = st.secrets["email-creds"]["smtp_pass"]

    sender_email = smtp_username

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)

        total_emails = len(data)
        progress_increment = 1 / total_emails

        for i, item in data.iterrows():
            receiver_email = item.email
            pdf_path = f"data/{item.loc['name']}.pdf"

            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            with open(pdf_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(pdf_path)}")
            message.attach(part)
            text = message.as_string()

            try:
                server.sendmail(sender_email, receiver_email, text)
                print(f"Email sent successfully to {receiver_email}")
            except Exception as e:
                print(f"Error sending email to {receiver_email}: {e}")

            bar.progress((i + 1) * progress_increment, text=f"Sent mail to {receiver_email}")

    time.sleep(1)
    bar.empty()

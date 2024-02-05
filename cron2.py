import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email():
    sender_email = 'aslal-salmi@hotmail.fr'
    receiver_email = 'salmi.ensa.ilsi@gmail.com'  # Replace with the recipient's email address
    subject = 'Subject here'
    message = 'Here is the message.'

    # Create a MIMEText object to represent the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Get email configuration from environment variables
        EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.office365.com")
        EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
        EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "aslal-salmi@hotmail.fr")
        EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "salmi@ensa123")
        EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", True)
        SERVER_EMAIL = EMAIL_HOST_USER
        
        # Connect to the SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        
        if EMAIL_USE_TLS:
            server.starttls()  # Enable TLS encryption
        
        # Login to your email account
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        
        # Close the connection
        server.quit()
        
        print("Email sent successfully.")
    except Exception as e:
        print(f"Email sending failed because of: {str(e)}")

if __name__ == "__main__":
    send_email()

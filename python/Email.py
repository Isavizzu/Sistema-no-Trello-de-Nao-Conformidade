import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email:
    def __init__(self, email, password):
        self.server = 'smtp.gmail.com'
        self.port = 587 
        self.email = email
        self.password = password


    def send_email(self, to, subject, body):
        mensagem = MIMEMultipart()
        mensagem['From'] = self.email
        mensagem['To'] = to
        mensagem['Subject'] = subject
        mensagem.attach(MIMEText(body, 'plain'))
        
        connection = smtplib.SMTP(self.server, self.port)
        connection.starttls()
        connection.login(self.email,self.password)
        connection.send_message(mensagem) 
        connection.quit() 





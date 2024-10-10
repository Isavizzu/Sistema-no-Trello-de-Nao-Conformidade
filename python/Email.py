import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Email:
    
    def __init__(self,email,password):
        self.email = email
        self.password =password
    

    def send_email(self, receiver_email, subject,body):
        message = MIMEMultipart()
        message["From"] = self.email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        try:
            with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:  
                server.starttls()  
                server.login(self.email, self.password)  
                server.sendmail(sender_email, receiver_email, message.as_string())  
            print("E-mail enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar o e-mail: {e}")

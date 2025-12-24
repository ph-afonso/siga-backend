from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
import threading

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMultiAlternatives(
            subject=data['email_subject'],
            body=data['email_body'], 
            to=[data['to_email']]
        )
        
        # 1. Anexa o HTML
        if 'email_html' in data:
            email.attach_alternative(data['email_html'], "text/html")

        # 2. (NOVO) Anexa Imagens (Logos, banners) via CID
        # O dicionário espera: {'nome_cid': dados_binarios}
        if 'email_images' in data:
            for cid_name, image_data in data['email_images'].items():
                logo = MIMEImage(image_data)
                logo.add_header('Content-ID', f'<{cid_name}>') # Ex: <logo>
                logo.add_header('Content-Disposition', 'inline', filename=f'{cid_name}.png')
                email.attach(logo)

        EmailThread(email).start()
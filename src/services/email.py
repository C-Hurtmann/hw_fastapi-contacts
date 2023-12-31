from pathlib import Path

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings


config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME='Constantine Zagorodnyi',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)

async def send_email(email: EmailStr, host: str):
    """
    Send verification letter to email.
    
    :param email: User email, which letter will be sent.
    :type email: EmailStr
    :param host: Host for verification link.
    :type host: str
    :rtype: None
    """
    try:
        verification_token = await auth_service.create_verification_token({'sub': email})
        message = MessageSchema(
            subject='MyHW13: Verify your email',
            recipients=[email],
            template_body={'host': host, 'token': verification_token},
            subtype=MessageType.html
        )
        fm = FastMail(config)
        await fm.send_message(message, template_name='verification_email.html')
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(email: EmailStr, password: str, host: str):
    """
    Send rest password letter. Send jwt with user email and new password hash.
    
    If user goes to the link, password will be changed.
    
    :param email: User email, which letter will be sent.
    :type email: EmailStr
    :param password: New password hash.
    :type password: str
    :param host: Host for verification link.
    :type host: str
    
    """
    hashed_password = auth_service.get_password_hash(password)
    reset_password_token = await auth_service.create_reset_password_token({'sub': email, 'pas': hashed_password})
    message = MessageSchema(
        subject='MyHW13: Peset password',
        recipients=[email],
        template_body={'host': host, 'token': reset_password_token},
        subtype=MessageType.html
    )
    fm = FastMail(config)
    await fm.send_message(message, template_name='reset_password_email.html')

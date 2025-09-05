from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# Alternative approach for development
def send_verification_email(user_inquiry):
    """Send verification email to user"""
    subject = "Verify Your Email Address - CPI Technologies"
    
    # Create verification link for development
    verification_link = f"http://127.0.0.1:8000/verify-email/{user_inquiry.verification_token}/"
    
    # HTML email content
    html_message = render_to_string('chatbot/verification_email.html', {
        'name': user_inquiry.name,
        'verification_link': verification_link,
        'service': user_inquiry.service,
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user_inquiry.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
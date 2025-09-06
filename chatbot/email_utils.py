   
    """Send verification email to user for i3Cert Training"""
    subject = "Verify Your Email Address - i3Cert Generative AI Training"
    
    # Create verification link for development
     verification_link = f"http://adedayo.pythonanywhere.com/verify-email/{user_inquiry.verification_token}/"

    # HTML email content - Updated for training focus
 
    html_message = render_to_string('chatbot/verification_email.html', {
        'name': user_inquiry.name,
        'verification_link': verification_link,
        'course': user_inquiry.service,
        'discount': "5%",  # Added discount information
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
        return False verification_link = f"http://adedayo.pythonanywhere.com/verify-email/{user_inquiry.verification_token}/"


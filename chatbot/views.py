from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from .models import Node, Option
from .utils import ask_openai
import json
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import UserProfile
import secrets
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail, EmailMessage


@ensure_csrf_cookie
def auth_page(request):
    """Render the authentication page with CSRF token"""
    return render(request, 'chatbot/auth.html')


@csrf_exempt  # Temporarily exempt for API calls, but better to handle properly
def register_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            
            # Extract data from request
            full_name = data.get('fullName', '')
            email = data.get('email', '')
            phone = data.get('phone', '')
            country = data.get('country', '')
            password = data.get('password', '')
            
            # Check if user already exists by email
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already exists'})
            
            # Generate a unique username
            base_username = email.split('@')[0]  # Use part before @
            username = base_username
            
            # Ensure username is unique by appending numbers if needed
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                # Safety check to prevent infinite loop
                if counter > 100:
                    # If we can't find a unique username, use a UUID
                    import uuid
                    username = f"user_{uuid.uuid4().hex[:8]}"
                    break
            
            # Create user
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password,
                first_name=full_name  # Store full name in first_name field
            )
            
            # Update user profile
            user_profile = user.userprofile
            user_profile.phone = phone
            user_profile.country = country
            user_profile.verification_token = secrets.token_urlsafe(32)
            user_profile.save()
            
            # Send verification email
            subject = 'Verify your CPI Technologies account'
            
            # Render HTML content
            html_message = render_to_string('verification_email.html', {
                'user': user,
                'token': user_profile.verification_token,
                'domain': request.get_host(),
            })
            
            # Create plain text version as fallback
            plain_message = f"""
            Hello {user.username},
            
            Thank you for registering with CPI Technologies. 
            Please verify your email address by visiting this link:
            
            http://{request.get_host()}/verify-email/{user_profile.verification_token}/
            
            If you didn't create an account with us, please ignore this email.
            """
            
            try:
                # Use EmailMessage to send HTML email
                email_msg = EmailMessage(
                    subject,
                    html_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                email_msg.content_subtype = "html"  # Set content type to HTML
                email_msg.send(fail_silently=False)
                
                return JsonResponse({'success': True, 'message': 'Registration successful. Please check your email to verify your account.'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error sending email: {str(e)}'})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



def verify_email(request, token):
    try:
        user_profile = UserProfile.objects.get(verification_token=token)
        user_profile.email_verified = True
        user_profile.verification_token = ''
        user_profile.save()
        return render(request, 'verification_success.html')
    except UserProfile.DoesNotExist:
        return render(request, 'verification_failed.html')


@csrf_exempt  # Temporarily exempt for API calls
def login_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # Find user by email instead of username
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid credentials'})
            
            # Authenticate using the username but check password
            user_auth = authenticate(request, username=user.username, password=password)
            
            if user_auth is not None:
                # Check if email is verified
                if user.userprofile.email_verified:
                    login(request, user_auth)
                    return JsonResponse({'success': True, 'message': 'Login successful'})
                else:
                    return JsonResponse({'success': False, 'message': 'Please verify your email before logging in.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid credentials'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
            
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def home(request):
    # Get the starting node (you might want to create a "start" node)
    start_node = Node.objects.first()  # Or use a specific starting node
    return render(request, "chatbot/index.html", {'start_message': start_node.message if start_node else "Hello! How can I help you?"})


@csrf_exempt
@require_POST
def reply(request):
    try:
        data = json.loads(request.body)
        user_input = data.get("message", "").strip().lower()
        current_node_id = data.get("current_node", None)
    except Exception:
        return JsonResponse({"response": "Invalid request format", "current_node": None}, status=400)
    
    bot_response = None
    next_node_id = None
    
    # Try to find a matching option from the current node
    if current_node_id:
        try:
            current_node = Node.objects.get(id=current_node_id)
            # Look for options that match the user input (case insensitive)
            option = Option.objects.filter(
                from_node=current_node, 
                keyword__iexact=user_input
            ).first()
            
            if option:
                bot_response = option.to_node.message
                next_node_id = option.to_node.id
        except (Node.DoesNotExist, Option.DoesNotExist):
            pass
    
    # If no option matched, try to find any option that matches (fallback)
    if not bot_response:
        option = Option.objects.filter(keyword__iexact=user_input).first()
        if option:
            bot_response = option.to_node.message
            next_node_id = option.to_node.id
    
    # If still no match, use OpenAI
    if not bot_response:
        bot_response = ask_openai(user_input)
        # Stay on the same node if using OpenAI
        next_node_id = current_node_id
    
    return JsonResponse({
        "response": bot_response,
        "current_node": next_node_id
    })


@login_required
def get_start_node(request):
    """API to get the starting node"""
    start_node = Node.objects.first()  # Or use a specific starting node
    return JsonResponse({
        "message": start_node.message if start_node else "Hello! How can I help you?",
        "current_node": start_node.id if start_node else None
    })


@login_required
def flow_editor(request):
    return render(request, "chatbot/editor.html")


def get_csrf_token(request):
    """API endpoint to get CSRF token"""
    return JsonResponse({'csrfToken': get_token(request)})
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Node, Option, UserInquiry
from .utils import ask_openai
from .email_utils import send_verification_email
import json
import re

# Store user session data (in production, use a proper session or database)
user_sessions = {}

def home(request):
    # Get the starting node
    start_node = Node.objects.filter(is_start=True).first() or Node.objects.first()
    return render(request, "chatbot/index.html", {'start_message': start_node.message if start_node else "Hello! How can I help you?"})

@csrf_exempt
@require_POST
def reply(request):
    try:
        data = json.loads(request.body)
        user_input = data.get("message", "").strip().lower()
        current_node_id = data.get("current_node", None)
        session_id = data.get("session_id", "")
    except Exception:
        return JsonResponse({"response": "Invalid request format", "current_node": None}, status=400)
    
    # Initialize session if it doesn't exist
    if session_id not in user_sessions:
        user_sessions[session_id] = {"name": "", "email": "", "service": "", "next_step": None, "show_services": True, "email_confirmed": False, "waiting_for_verification": False}
    
    # Check if user is waiting for email verification
    if user_sessions[session_id].get("waiting_for_verification"):
        # Check if email has been verified in the database
        try:
            user_inquiry = UserInquiry.objects.get(session_id=session_id)
            if user_inquiry.is_verified:
                user_sessions[session_id]["waiting_for_verification"] = False
                bot_response = "Great! Your email has been verified. How can I help you continue?"
            else:
                bot_response = "Please check your email and verify your address to continue the conversation. We've sent a verification link to your email."
        except UserInquiry.DoesNotExist:
            bot_response = "Please check your email and verify your address to continue the conversation. We've sent a verification link to your email."
        
        return JsonResponse({
            "response": bot_response,
            "current_node": current_node_id,
            "session_id": session_id,
            "show_service_options": False,
            "waiting_for_verification": user_sessions[session_id].get("waiting_for_verification", False)
        })
    
    bot_response = None
    next_node_id = None
    
    # Get current node if available
    current_node = None
    if current_node_id:
        try:
            current_node = Node.objects.get(id=current_node_id)
        except Node.DoesNotExist:
            pass
    
    # Check if user is in the middle of a flow
    next_step = user_sessions[session_id].get("next_step")
    show_services = user_sessions[session_id].get("show_services", False)
    
    # Handle name collection after service selection
    if next_step == "ask_name":
        user_sessions[session_id]["name"] = user_input
        user_sessions[session_id]["next_step"] = "ask_email"
        user_sessions[session_id]["show_services"] = False
        
        bot_response = f"Thank you {user_input}. Can you please provide the best email for us to reach you?"
        next_node_id = current_node_id if current_node_id else None
    
    # Handle email collection
    elif next_step == "ask_email":
        # Validate email format
        if re.match(r"[^@]+@[^@]+\.[^@]+", user_input):
            # Check if email already exists in database
            try:
                existing_inquiry = UserInquiry.objects.get(email=user_input)
                
                if existing_inquiry.is_verified:
                    # Email already verified, continue conversation
                    user_sessions[session_id]["email"] = user_input
                    user_sessions[session_id]["next_step"] = None
                    user_sessions[session_id]["show_services"] = False
                    user_sessions[session_id]["email_confirmed"] = True
                    
                    # Update current session with existing user info
                    user_sessions[session_id]["name"] = existing_inquiry.name
                    user_sessions[session_id]["service"] = existing_inquiry.service
                    
                    bot_response = f"Welcome back {existing_inquiry.name}! Your email is already verified. How can I help you with our {existing_inquiry.service} services today?"
                    next_node_id = current_node_id if current_node_id else None
                else:
                    # Email exists but not verified, continue with confirmation
                    user_sessions[session_id]["email"] = user_input
                    user_sessions[session_id]["next_step"] = "confirm_email"
                    user_sessions[session_id]["show_services"] = False
                    
                    bot_response = f"Thank you. Just to make sure we got it right, your email is {user_input}. Is this correct? (Please respond with 'yes' or 'no')"
                    next_node_id = current_node_id if current_node_id else None
                    
            except UserInquiry.DoesNotExist:
                # New email
                user_sessions[session_id]["email"] = user_input
                user_sessions[session_id]["next_step"] = "confirm_email"
                user_sessions[session_id]["show_services"] = False
                
                bot_response = f"Thank you. Just to make sure we got it right, your email is {user_input}. Is this correct? (Please respond with 'yes' or 'no')"
                next_node_id = current_node_id if current_node_id else None
        else:
            bot_response = "That doesn't look like a valid email address. Please provide a valid email."
            next_node_id = current_node_id if current_node_id else None
    
    # Handle email confirmation
    elif next_step == "confirm_email":
        if user_input in ["yes", "y", "correct", "right"]:
            user_sessions[session_id]["next_step"] = None
            user_sessions[session_id]["show_services"] = False
            user_sessions[session_id]["email_confirmed"] = True
            
            # Check if email already exists in database
            try:
                existing_inquiry = UserInquiry.objects.get(email=user_sessions[session_id]["email"])
                
                if existing_inquiry.is_verified:
                    # Email already verified, continue conversation
                    bot_response = f"Welcome back {existing_inquiry.name}! Your email is already verified. How can I help you with our {existing_inquiry.service} services today?"
                    next_node_id = current_node_id if current_node_id else None
                else:
                    # Update existing record
                    existing_inquiry.name = user_sessions[session_id]["name"]
                    existing_inquiry.service = user_sessions[session_id].get("service", "general inquiry")
                    existing_inquiry.session_id = session_id
                    existing_inquiry.email_confirmed = True
                    existing_inquiry.save()
                    
                    # Send verification email
                    if send_verification_email(existing_inquiry):
                        user_sessions[session_id]["waiting_for_verification"] = True
                        bot_response = "Perfect! We've sent a verification email to your address. Please check your inbox and click the verification link to continue our conversation. You'll need to verify your email before we can proceed."
                    else:
                        bot_response = "We encountered an issue sending the verification email. Please try again later or contact support."
                    
            except UserInquiry.DoesNotExist:
                # Create new record
                try:
                    user_inquiry = UserInquiry.objects.create(
                        name=user_sessions[session_id]["name"],
                        email=user_sessions[session_id]["email"],
                        service=user_sessions[session_id].get("service", "general inquiry"),
                        session_id=session_id,
                        email_confirmed=True
                    )
                    
                    # Send verification email
                    if send_verification_email(user_inquiry):
                        user_sessions[session_id]["waiting_for_verification"] = True
                        bot_response = "Perfect! We've sent a verification email to your address. Please check your inbox and click the verification link to continue our conversation. You'll need to verify your email before we can proceed."
                    else:
                        bot_response = "We encountered an issue sending the verification email. Please try again later or contact support."
                        
                except Exception as e:
                    print(f"Error saving user inquiry: {e}")
                    bot_response = "Sorry, we encountered an error. Please try again."
            
            next_node_id = current_node_id if current_node_id else None
        
        elif user_input in ["no", "n", "incorrect", "wrong"]:
            user_sessions[session_id]["next_step"] = "ask_email"
            user_sessions[session_id]["show_services"] = False
            user_sessions[session_id]["email"] = ""  # Clear the email
            
            bot_response = "I apologize for the mistake. Please provide your email again."
            next_node_id = current_node_id if current_node_id else None
        
        else:
            bot_response = "Please respond with 'yes' or 'no'. Is your email correct?"
            next_node_id = current_node_id if current_node_id else None
    
    # Handle service selection (from buttons or text)
    elif not next_step and user_input in ["training course", "digital services", "it services", "other service", "training", "digital", "it", "other"]:
        # Map variations to the standard service names
        service_map = {
            "training": "training course",
            "digital": "digital services", 
            "it": "it services",
            "other": "other service"
        }
        
        service = service_map.get(user_input, user_input)
        user_sessions[session_id]["service"] = service
        user_sessions[session_id]["next_step"] = "ask_name"
        user_sessions[session_id]["show_services"] = False
        
        # Thank user for their selection
        bot_response = f"Great! You're interested in our {service}. Before we continue, we'd like to quickly get some basic details about you. What is your name?"
        next_node_id = current_node_id if current_node_id else None
    
    # Handle initial message - show service options if no next_step
    elif not next_step and show_services:
        # If user typed something that's not a service, still show service options
        user_sessions[session_id]["show_services"] = True
        
        bot_response = "Please select one of our services to continue:"
        next_node_id = current_node_id if current_node_id else None
    
    # If no special handling, try to find a matching option from the current node
    elif current_node and not next_step:
        try:
            # Standard option matching for other nodes
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
    if not bot_response and not next_step:
        option = Option.objects.filter(keyword__iexact=user_input).first()
        if option:
            bot_response = option.to_node.message
            next_node_id = option.to_node.id
    
    # If still no match, use OpenAI but still show service options if needed
    if not bot_response:
        if not next_step and user_sessions[session_id].get("show_services", True):
            user_sessions[session_id]["show_services"] = True
            bot_response = "Please select one of our services to continue:"
        else:
            bot_response = ask_openai(user_input)
        # Stay on the same node
        next_node_id = current_node_id
    
    # Add flag to indicate if service options should be shown
    show_service_options = user_sessions[session_id].get("show_services", False) and not next_step
    
    return JsonResponse({
        "response": bot_response,
        "current_node": next_node_id,
        "session_id": session_id,
        "show_service_options": show_service_options,
        "waiting_for_verification": user_sessions[session_id].get("waiting_for_verification", False)
    })

def check_verification_status(request):
    """Check if email has been verified for a session"""
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'verified': False})
    
    try:
        user_inquiry = UserInquiry.objects.get(session_id=session_id)
        return JsonResponse({
            'verified': user_inquiry.is_verified,
            'email': user_inquiry.email
        })
    except UserInquiry.DoesNotExist:
        return JsonResponse({'verified': False})

def verify_email(request, token):
    """Handle email verification"""
    try:
        user_inquiry = UserInquiry.objects.get(verification_token=token)
        user_inquiry.is_verified = True
        user_inquiry.email_confirmed = True  # Also update email_confirmed field
        user_inquiry.save()
        
        # Update session to allow conversation to continue
        session_id = user_inquiry.session_id
        if session_id in user_sessions:
            user_sessions[session_id]["waiting_for_verification"] = False
        
        return render(request, 'chatbot/verification_success.html', {
            'name': user_inquiry.name,
            'email': user_inquiry.email,
            'session_id': session_id  # Pass session_id to the template
        })
    except UserInquiry.DoesNotExist:
        return render(request, 'chatbot/verification_error.html', {
            'error': 'Invalid verification token'
        })

def get_start_node(request):
    """API to get the starting node"""
    start_node = Node.objects.filter(is_start=True).first() or Node.objects.first()
    
    # If no start node exists, create a default one
    if not start_node:
        start_node = Node.objects.create(
            name="welcome",
            message="Hello! Welcome to CPI Technologies. How can I help you achieve your goal today?",
            is_start=True
        )
    
    return JsonResponse({
        "message": start_node.message,
        "current_node": start_node.id,
        "show_service_options": True
    })

def flow_editor(request):
    return render(request, "chatbot/editor.html")
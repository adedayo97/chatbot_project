from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Node, Option
from .utils import ask_openai
import json

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

def get_start_node(request):
    """API to get the starting node"""
    start_node = Node.objects.first()  # Or use a specific starting node
    return JsonResponse({
        "message": start_node.message if start_node else "Hello! How can I help you?",
        "current_node": start_node.id if start_node else None
    })

def flow_editor(request):
    return render(request, "chatbot/editor.html")
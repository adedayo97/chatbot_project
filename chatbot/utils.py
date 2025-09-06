import os
from openai import OpenAI
from django.conf import settings
from .models import Node, Option
import re

# ✅ Initialize OpenAI client correctly for PythonAnywhere
client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))

# utils.py - Update the ask_openai function

def ask_openai(user_input, current_node_id=None):
    """
    Generate a response using OpenAI API with context from nodes and i3Cert Training info
    """
    try:
        # Get relevant nodes based on user input
        relevant_nodes = find_relevant_nodes(user_input, current_node_id)
        
        # Get node context for the prompt
        node_context = get_node_context(relevant_nodes)
        
        # i3Cert Training content from the document
        training_context = """
        i3Cert Generative AI Certification Pathway by CPI Technologies:

        The program provides a progressive learning journey for professionals, students, 
        and organizations to master Generative Artificial Intelligence.

        Certification Levels:
        1. Certified Generative AI Fundamentals (CGAF) - Entry-Level (8 hours)
        2. Certified Generative AI Associate (CGAA) - Intermediate (32 hours) 
        3. Certified Generative AI Professional (CGAP) - Advanced (60 hours)
        4. Certified Generative AI Expert (CGAE) - Expert-Level (80-100 hours)

        Key Benefits:
        - Future-Proof Your Career: Over 60% of jobs will be influenced by AI in 5 years
        - Practical, Hands-On Learning: Build chatbots, AI apps, automation workflows
        - Structured Learning Pathway: From basic literacy to enterprise deployment
        - Cross-Industry Relevance: Education, healthcare, business, government, creativity
        - Global Recognition & Networking: Internationally respected certifications
        - Responsible & Ethical AI Training: Learn secure and ethical use of AI

        Each certification includes:
        - Comprehensive course materials
        - Hands-on labs and projects
        - Industry-recognized certification
        - Digital badge and certificate
        - Access to global community

        Contact Information:
        - Phone: +1224-201-8888
        - Email: sales@cpitechinc.com
        - Website: www.cpitechinc.com
        - Address: 1900 N Austin Avenue, suite 210, Chicago 60639 IL
        """
        
        # Create a comprehensive system prompt
        system_prompt = f"""You are a friendly AI training advisor for CPI Technologies' i3Cert Generative AI Certification Pathway.

TRAINING PROGRAM INFORMATION:
{training_context}

RELEVANT COURSE INFORMATION:
{node_context}

RESPONSE GUIDELINES:
1. Respond primarily based on the i3Cert Training context provided above
2. If the query is unrelated to AI training, politely redirect to our certification programs
3. Keep responses concise (2-3 paragraphs maximum)
4. Maintain a professional, helpful tone focused on education
5. If asking follow-up questions, make them open-ended to continue the conversation
6. For pricing inquiries, explain that it varies by program and offer to provide details
7. For technical questions, offer to connect with our training specialists

IMPORTANT: If you cannot answer based on the context, say "I specialize in CPI Technologies' i3Cert Generative AI training programs. How can I help you with our certification pathway?"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            max_tokens=350,
            top_p=0.9
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        error_msg = f"I apologize, but I'm experiencing technical difficulties. Please try again later or contact our training support team."
        # Log the error for debugging
        print(f"OpenAI API Error: {str(e)}")
        return error_msg


def find_relevant_nodes(user_input, current_node_id=None):
    """
    Find nodes that are relevant to the user's query, prioritizing current node options
    """
    relevant_nodes = []
    user_input_lower = user_input.lower()
    
    # First, check options from the current node if available
    if current_node_id:
        try:
            current_node = Node.objects.get(id=current_node_id)
            options = Option.objects.filter(from_node=current_node)
            
            for option in options:
                if option.keyword.lower() in user_input_lower:
                    try:
                        relevant_nodes.append(option.to_node)
                    except Node.DoesNotExist:
                        pass
        except (Node.DoesNotExist, Option.DoesNotExist):
            pass
    
    # If no relevant options from current node, search all nodes
    if not relevant_nodes:
        keyword_groups = {
            'it_consulting': ['consulting', 'strategy', 'planning', 'infrastructure', 
                             'governance', 'compliance', 'it strategy', 'digital transformation'],
            'software_dev': ['software', 'development', 'application', 'app', 'web', 
                           'mobile', 'api', 'programming', 'custom software', 'develop'],
            'cloud_services': ['cloud', 'aws', 'azure', 'google cloud', 'migration', 
                             'devops', 'infrastructure', 'cloud computing'],
            'cybersecurity': ['security', 'cyber', 'protection', 'hack', 'firewall', 
                            'compliance', 'gdpr', 'hipaa', 'security', 'data protection'],
            'data_analytics': ['data', 'analytics', 'business intelligence', 'bi', 
                             'reporting', 'dashboard', 'insights'],
            'managed_services': ['managed', 'support', 'maintenance', 'outsourcing', 
                               'it support', 'helpdesk'],
            'services': ['services', 'offerings', 'solutions', 'what can you do', 
                       'what do you offer'],
            'about': ['about', 'company', 'who are you', 'background', 'history', 
                    'mission', 'vision'],
            'contact': ['contact', 'phone', 'email', 'address', 'location', 
                      'get in touch', 'reach', 'call'],
            'pricing': ['price', 'cost', 'how much', 'pricing', 'quote', 'budget'],
            'case_studies': ['examples', 'portfolio', 'case studies', 'clients', 
                           'success stories', 'testimonials']
        }
        
        for node_name, keywords in keyword_groups.items():
            if any(keyword in user_input_lower for keyword in keywords):
                try:
                    node = Node.objects.get(name=node_name)
                    if node not in relevant_nodes:
                        relevant_nodes.append(node)
                except Node.DoesNotExist:
                    pass
    
    # If still no relevant nodes, return some general nodes
    if not relevant_nodes:
        try:
            general_nodes = ['greeting', 'services', 'about']
            for node_name in general_nodes:
                try:
                    node = Node.objects.get(name=node_name)
                    relevant_nodes.append(node)
                except Node.DoesNotExist:
                    pass
        except:
            pass
    
    return relevant_nodes


def get_node_context(relevant_nodes):
    """
    Extract context from relevant nodes for the OpenAI prompt
    """
    if not relevant_nodes:
        return "No specific service information available. Please refer to general company information."
    
    context_parts = []
    for node in relevant_nodes:
        context_parts.append(f"{node.message}")
    
    return "\n\n".join(context_parts)


def extract_keywords(text):
    """
    Extract potential keywords from text to help with node matching
    """
    text = text.lower()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = re.findall(r'\b[a-z]{3,}\b', text)
    keywords = [word for word in words if word not in stop_words]
    return set(keywords)

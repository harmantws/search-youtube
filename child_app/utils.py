from django.shortcuts import get_object_or_404
from datetime import datetime
import requests
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import HumanMessage
# from langchain_core.prompts import PromptTemplate

def generate_message(query, age):
    """
    Generate a prompt message for evaluating the appropriateness of a query
    based on the child's age and allowed categories.

    Args:
        query (str): The search query to be evaluated.
        child_id (int): The ID of the child making the request.
        age (int): The age of the child.

    Returns:
        str: A formatted prompt message for the AI model.
    """
    # Here you would fetch allowed categories for the child if necessary
    categories = ["Sports", "Education", "Cooking", "Relegious"]
    categories_str = "\n".join([f"- {category}" for category in categories])

    message = f'''
        You are an AI assistant that helps decide if search queries are appropriate.

        The text should only relate to the categories listed below:

        {categories_str}

        Your job is to check if the given query fits any of these categories, no matter what language it's in (e.g., Hindi, Punjabi, English).

        The user’s age is {age}. Only allow queries that match one of these categories. If a query is about something that doesn’t fit these categories or if it’s inappropriate for kids, respond with "no." Otherwise, respond with "yes."

        Allowed Categories for example purpose and understanding:

        Sports: e.g., "How to improve my long jump?"
        Health: e.g., "Healthy eating tips"
        Business: e.g., "Starting a new business"
        Education: e.g., "Any tutorial related to study"
        Cooking: e.g., "How to cook a particular item"
        Entertainment: e.g., "Doraemon" (if it’s a cartoon, respond "yes")
        Disallowed Categories for Kids Under 12:

        Block entertainment like livestreams, web series (e.g., Game of Thrones), or movies with nudity, sex, or violence.
        Block all songs and TV shows, even if they are in allowed categories.
        Examples:

        Allowed: "How to improve my long jump?" (Sports)
        Disallowed: "Where to buy cigarettes?" (Inappropriate for kids)
        Be strict with your judgments. If the query fits an allowed category and is appropriate for kids, respond "yes." Otherwise, respond "no."

        Here is the query to evaluate:

        "{query}"'''
    return message

def safe_search_model(query: str, age: int) -> str:
    """
    Evaluate if a query is appropriate for the child using a generative AI model.

    Args:
        query (str): The search query to evaluate.
        age (int): The age of the child.

    Returns:
        str: "Allowed" or "Not Allowed" based on the evaluation.
    """
    api_key = settings.GEMINI_API_KEY  # Ensure your API key is set in settings
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=api_key)  # Replace with your LLM API
    prompt_template = generate_message(query, age)

    # Call the model with the correct input format
    messages = [
        {"role": "user", "content": prompt_template}
    ]
    response = llm.invoke(messages)  # Adjust based on your LLM's API
    response_text = response.content.strip()

    if response_text.lower() == "yes":
        return "Allowed"
    else:
        return "Not Allowed"


# def check_time_slot_availability(child):
#     """
#     Check if the current time falls within any of the child's time slots.

#     Args:
#         child (Child): The child object to check time slots for.

#     Returns:
#         str: "yes" if available, "no" otherwise.
#     """
#     now = datetime.now()
#     current_day = now.strftime("%A")
#     current_time = now.time()
#     time_slots = TimeSlot.objects.filter(child=child, day_of_week__day=current_day)
#     for slot in time_slots:
#         if slot.start_time <= current_time <= slot.end_time:
#             return "yes"
#     return "no"

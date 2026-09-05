"""
MindSense AI - Mental Health Chatbot Model

Purpose:
    - Receive a user's message
    - Understand basic mental-health-related keywords
    - Consider the user's reported condition
    - Generate a supportive response
    - Suggest simple, practical steps
    - Detect situations where immediate professional help may be needed

IMPORTANT:
    This is an educational prototype.
    It is NOT a medical diagnosis or treatment system.
"""

# ============================================================
# 1. IMPORTS
# ============================================================

import re
from datetime import datetime


# ============================================================
# 2. RESPONSE DATABASE
# ============================================================

RESPONSES = {

    "stress": {
        "keywords": [
            "stress",
            "stressed",
            "pressure",
            "overwhelmed",
            "workload",
            "tension",
            "burden"
        ],

        "responses": [
            "It sounds like you may be feeling under a lot of pressure. You don't have to solve everything at once.",
            "I understand that things can feel overwhelming sometimes. Let's take it one small step at a time.",
            "You seem to be dealing with some stress right now. Taking a short break and focusing on one task can help."
        ],

        "solutions": [
            "Take 5 slow and deep breaths.",
            "Break your biggest task into smaller tasks.",
            "Take a short walk or step away from your screen.",
            "Write down the things that are worrying you.",
            "Try to maintain a regular sleep schedule."
        ]
    },


    "anxiety": {
        "keywords": [
            "anxiety",
            "anxious",
            "worried",
            "worry",
            "nervous",
            "panic",
            "fear",
            "scared",
            "uneasy"
        ],

        "responses": [
            "It sounds like you may be experiencing some anxiety. You're not alone in feeling this way.",
            "I hear you. When worries become intense, focusing on the present moment can sometimes help.",
            "It seems like something is making you feel anxious. Let's focus on what you can manage right now."
        ],

        "solutions": [
            "Try slow breathing: breathe in for 4 seconds and out for 6 seconds.",
            "Look around and identify five things you can see.",
            "Focus on one thing you can control right now.",
            "Talk to someone you trust about how you're feeling.",
            "Reduce excessive caffeine if it makes you feel more anxious."
        ]
    },


    "sadness": {
        "keywords": [
            "sad",
            "sadness",
            "unhappy",
            "cry",
            "crying",
            "lonely",
            "alone",
            "empty",
            "down",
            "upset"
        ],

        "responses": [
            "I'm sorry that you're going through a difficult moment. Your feelings are important.",
            "It sounds like you're having a hard time. You don't have to handle everything by yourself.",
            "Thank you for sharing how you're feeling. Sometimes simply talking about it is an important first step."
        ],

        "solutions": [
            "Talk to a trusted friend or family member.",
            "Try spending a little time outside.",
            "Do one small activity that you normally enjoy.",
            "Write down what you're feeling.",
            "Give yourself permission to rest."
        ]
    },


    "sleep": {
        "keywords": [
            "sleep",
            "sleeping",
            "insomnia",
            "tired",
            "fatigue",
            "awake",
            "sleepless",
            "rest"
        ],

        "responses": [
            "It sounds like your sleep may be affecting how you're feeling.",
            "Getting enough quality sleep can be important for emotional well-being.",
            "If your sleep has been difficult recently, let's focus on creating a calmer bedtime routine."
        ],

        "solutions": [
            "Try going to bed and waking up at similar times.",
            "Reduce screen use before sleeping.",
            "Keep your bedroom quiet and comfortable.",
            "Avoid heavy caffeine late in the day.",
            "Try a short breathing exercise before bed."
        ]
    },


    "motivation": {
        "keywords": [
            "motivation",
            "motivated",
            "lazy",
            "productive",
            "productivity",
            "focus",
            "concentrate",
            "concentration"
        ],

        "responses": [
            "It sounds like you're finding it difficult to stay motivated. That's something many people experience.",
            "You don't need to accomplish everything at once. Small progress still counts.",
            "When motivation is low, starting with a very small task can make things feel easier."
        ],

        "solutions": [
            "Choose one small task to complete first.",
            "Use a 10-minute timer and work only until it ends.",
            "Remove distractions from your workspace.",
            "Celebrate small achievements.",
            "Take regular breaks instead of forcing yourself to work continuously."
        ]
    },


    "positive": {
        "keywords": [
            "happy",
            "good",
            "great",
            "excited",
            "positive",
            "better",
            "calm",
            "peaceful",
            "wonderful"
        ],

        "responses": [
            "I'm glad to hear that you're feeling positive.",
            "That's wonderful. Recognizing positive moments can be valuable for your well-being.",
            "It's great that you're feeling better. Try to notice what helped you reach this state."
        ],

        "solutions": [
            "Write down what made today better.",
            "Spend some time doing something you enjoy.",
            "Share your positive experience with someone you trust.",
            "Keep practicing habits that support your well-being."
        ]
    }
}


# ============================================================
# 3. CONDITION-SPECIFIC INFORMATION
# ============================================================

CONDITION_MESSAGES = {

    "stress": (
        "Your previous check-in suggests that stress may be an area "
        "worth paying attention to."
    ),

    "anxiety": (
        "Your previous check-in suggests that anxiety may be "
        "something you could reflect on."
    ),

    "depression": (
        "Your previous check-in suggests that your mood may need "
        "some additional attention and care."
    ),

    "balanced": (
        "Your previous check-in looked fairly balanced. "
        "We can still talk about anything that is bothering you."
    ),

    "moderate": (
        "Your previous check-in showed some areas that may benefit "
        "from additional attention."
    )
}


# ============================================================
# 4. EMERGENCY / SAFETY KEYWORDS
# ============================================================

SAFETY_KEYWORDS = [
    "suicide",
    "kill myself",
    "kill me",
    "end my life",
    "want to die",
    "don't want to live",
    "do not want to live",
    "self harm",
    "self-harm",
    "hurt myself",
    "harm myself"
]


# ============================================================
# 5. CLEAN USER MESSAGE
# ============================================================

def clean_message(message):
    """
    Convert user input into a simple format
    so keyword matching becomes easier.
    """

    if not message:
        return ""

    message = message.lower()

    # Remove unnecessary punctuation
    message = re.sub(r"[^a-zA-Z0-9\s-]", "", message)

    # Remove extra spaces
    message = re.sub(r"\s+", " ", message).strip()

    return message


# ============================================================
# 6. CHECK SAFETY MESSAGE
# ============================================================

def check_safety(message):
    """
    Check whether the user message contains
    high-risk phrases.

    Returns True if a safety concern is detected.
    """

    message = clean_message(message)

    for keyword in SAFETY_KEYWORDS:

        if keyword in message:
            return True

    return False


# ============================================================
# 7. DETECT USER'S EMOTION / TOPIC
# ============================================================

def detect_topic(message):

    message = clean_message(message)

    detected_topics = []

    for topic, data in RESPONSES.items():

        for keyword in data["keywords"]:

            if keyword in message:

                detected_topics.append(topic)

                break

    return detected_topics


# ============================================================
# 8. GET CONDITION INFORMATION
# ============================================================

def get_condition_message(condition):

    if not condition:
        return ""

    condition = condition.lower().strip()

    if condition in CONDITION_MESSAGES:

        return CONDITION_MESSAGES[condition]

    return (
        "Based on your previous check-in, we can use this conversation "
        "to understand how you're feeling today."
    )


# ============================================================
# 9. GENERATE SOLUTION
# ============================================================

def get_solution(topic):

    if topic not in RESPONSES:

        return (
            "Try taking a short break, drinking some water, "
            "and talking with someone you trust."
        )

    solutions = RESPONSES[topic]["solutions"]

    # Select first solution for predictable prototype behavior
    return solutions[0]


# ============================================================
# 10. GENERATE MAIN RESPONSE
# ============================================================

def generate_response(message, condition=None):

    """
    Main chatbot function.

    Parameters:
        message   -> User's message
        condition -> Condition from previous check-in

    Returns:
        Dictionary containing chatbot response information.
    """

    original_message = message

    message = clean_message(message)

    # --------------------------------------------------------
    # Empty message
    # --------------------------------------------------------

    if not message:

        return {
            "success": False,
            "message": "Please tell me a little about how you're feeling."
        }


    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if check_safety(message):

        return {
            "success": True,
            "type": "safety",
            "message": (
                "I'm really sorry that you're going through this. "
                "You deserve support, and you don't have to handle "
                "this alone."
            ),
            "solution": (
                "Please contact a trusted person or a qualified mental "
                "health professional right now. If you are in immediate "
                "danger, contact your local emergency service or go to "
                "the nearest emergency department."
            ),
            "timestamp": datetime.now().isoformat()
        }


    # --------------------------------------------------------
    # Detect topic
    # --------------------------------------------------------

    topics = detect_topic(message)


    # --------------------------------------------------------
    # No specific topic detected
    # --------------------------------------------------------

    if not topics:

        condition_text = get_condition_message(condition)

        return {
            "success": True,
            "type": "general",
            "message": (
                "Thank you for sharing that with me. "
                "I'm here to listen and help you think through it."
            ),
            "condition_context": condition_text,
            "solution": (
                "Try describing what has been bothering you most "
                "today, and we can take it one step at a time."
            ),
            "timestamp": datetime.now().isoformat()
        }


    # --------------------------------------------------------
    # Use first detected topic
    # --------------------------------------------------------

    topic = topics[0]

    topic_data = RESPONSES[topic]

    response_text = topic_data["responses"][0]

    solution = get_solution(topic)

    condition_text = get_condition_message(condition)


    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "success": True,
        "type": topic,
        "message": response_text,
        "condition_context": condition_text,
        "solution": solution,
        "detected_topics": topics,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# 11. SIMPLE CHAT FUNCTION
# ============================================================

def chat(message, condition=None):

    """
    Simple function for Flask.

    Example:

        result = chat(
            "I am feeling very stressed",
            "stress"
        )
    """

    result = generate_response(
        message=message,
        condition=condition
    )

    return result


# ============================================================
# 12. TEST THE MODEL DIRECTLY
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MindSense AI - Mental Health Chatbot")
    print("=" * 60)

    print("Type 'exit' to stop.")
    print()

    # Demo condition
    user_condition = "stress"

    while True:

        user_message = input("You: ")

        if user_message.lower() == "exit":
            print("MindSense AI: Take care of yourself. Goodbye!")
            break

        result = chat(
            user_message,
            user_condition
        )

        print()
        print("MindSense AI:")

        print(result["message"])

        if result.get("condition_context"):
            print()
            print(result["condition_context"])

        if result.get("solution"):
            print()
            print("💡 Suggestion:")
            print(result["solution"])

        print()
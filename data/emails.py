import random

EMAILS = [
    {
        "email_id": "E001",
        "sender": "john.smith@example.com",
        "subject": "URGENT: Cannot access my account - locked out for 3 days!",
        "body": (
            "Hi Support Team,\n\n"
            "My name is John Smith. I have been locked out of my account for 3 days now and "
            "I have an important presentation tomorrow that requires access to my files. "
            "I tried resetting my password but the reset email never arrives. "
            "This is extremely urgent. Please help immediately!\n\n"
            "Account email: john.smith@example.com\n\nRegards,\nJohn"
        ),
        "timestamp": "2024-03-15T09:23:00Z",
        "ground_truth": {
            "urgency": "critical",
            "category": "account",
            "customer_name": "John Smith",
            "primary_complaint": "Locked out of account for 3 days, password reset email not received",
        },
    },
    {
        "email_id": "E002",
        "sender": "priya.patel@gmail.com",
        "subject": "Question about my invoice from last month",
        "body": (
            "Hello,\n\n"
            "I noticed my invoice for February seems a bit higher than usual. "
            "I was charged $89.99 but I thought my plan was $69.99/month. "
            "Could you clarify why there's a $20 difference? No rush, just want to understand.\n\n"
            "My name is Priya Patel, account #PP-4421.\n\nThanks!"
        ),
        "timestamp": "2024-03-15T11:00:00Z",
        "ground_truth": {
            "urgency": "low",
            "category": "billing",
            "customer_name": "Priya Patel",
            "primary_complaint": "Invoice $20 higher than expected plan price",
        },
    },
    {
        "email_id": "E003",
        "sender": "marcus.t@business.org",
        "subject": "App keeps crashing when I upload files",
        "body": (
            "Hey Support,\n\n"
            "My name is Marcus Thompson. For the past two days your app crashes every time "
            "I try to upload files larger than 10MB. I get error code ERR_504. "
            "I'm on Windows 11, Chrome version 122. This is blocking my daily work.\n\n"
            "Please fix this ASAP.\nMarcus Thompson"
        ),
        "timestamp": "2024-03-15T14:10:00Z",
        "ground_truth": {
            "urgency": "high",
            "category": "technical",
            "customer_name": "Marcus Thompson",
            "primary_complaint": "App crashes on file uploads over 10MB with error ERR_504",
        },
    },
    {
        "email_id": "E004",
        "sender": "lisa.k@shoppers.net",
        "subject": "Where is my order #78234?",
        "body": (
            "Hi,\n\n"
            "I'm Lisa Kim and I placed order #78234 on March 5th. "
            "The estimated delivery was March 12th but it still hasn't arrived. "
            "The tracking page just says 'In Transit' with no updates since March 10th. "
            "Can you check what's happening?\n\nThanks,\nLisa"
        ),
        "timestamp": "2024-03-15T16:45:00Z",
        "ground_truth": {
            "urgency": "medium",
            "category": "shipping",
            "customer_name": "Lisa Kim",
            "primary_complaint": "Order #78234 delayed, no tracking update since March 10th",
        },
    },
    {
        "email_id": "E005",
        "sender": "carlos.r@personal.com",
        "subject": "How do I export my data?",
        "body": (
            "Hello,\n\n"
            "Quick question — I want to export all my data from your platform. "
            "Is there a way to do this in bulk? I looked in Settings but couldn't find it. "
            "No urgency, just planning ahead.\n\nBest,\nCarlos Reyes"
        ),
        "timestamp": "2024-03-16T09:05:00Z",
        "ground_truth": {
            "urgency": "low",
            "category": "general",
            "customer_name": "Carlos Reyes",
            "primary_complaint": "Cannot find bulk data export option in Settings",
        },
    },
    {
        "email_id": "E006",
        "sender": "ananya.m@corp.in",
        "subject": "CRITICAL: Production system down, data loss risk",
        "body": (
            "URGENT URGENT URGENT\n\n"
            "I am Ananya Mehta, CTO at CorpTech. Our production integration with your API "
            "went down 2 hours ago. We are unable to process payments and risk losing customer "
            "data. We are a paying enterprise customer. Every minute costs us thousands.\n\n"
            "We need an engineer on this NOW. Contact: +91-9876543210\nAnanya Mehta"
        ),
        "timestamp": "2024-03-16T13:30:00Z",
        "ground_truth": {
            "urgency": "critical",
            "category": "technical",
            "customer_name": "Ananya Mehta",
            "primary_complaint": "Production API integration down for 2 hours, payment processing halted",
        },
    },
    {
        "email_id": "E007",
        "sender": "sam.w@email.com",
        "subject": "Wrong item delivered",
        "body": (
            "Hi there,\n\n"
            "My name is Sam Wilson. I ordered the blue version of the XR-5 headphones "
            "but received the red version. Order #56901. "
            "I'd like to exchange it for the correct color. Please advise on the process.\n\nSam"
        ),
        "timestamp": "2024-03-16T15:00:00Z",
        "ground_truth": {
            "urgency": "medium",
            "category": "shipping",
            "customer_name": "Sam Wilson",
            "primary_complaint": "Wrong color item delivered, wants exchange for correct variant",
        },
    },
    {
        "email_id": "E008",
        "sender": "nina.b@freelance.io",
        "subject": "Charged twice for same subscription",
        "body": (
            "Hello Support,\n\n"
            "I'm Nina Brown. I've just noticed I was charged twice for my subscription "
            "this month — $49.99 on March 1st AND $49.99 on March 3rd. "
            "That's a double charge and I need a refund for one of them please.\n\n"
            "My account: nina.b@freelance.io\nNina"
        ),
        "timestamp": "2024-03-17T08:20:00Z",
        "ground_truth": {
            "urgency": "high",
            "category": "billing",
            "customer_name": "Nina Brown",
            "primary_complaint": "Double charged $49.99 for subscription in same month",
        },
    },
]


def get_email(email_id: str = None) -> dict:
    """Return a specific email or a random one."""
    if email_id:
        for e in EMAILS:
            if e["email_id"] == email_id:
                return e
    return random.choice(EMAILS)


def get_all_emails() -> list:
    return EMAILS

import os
import json

# Default templates
DEFAULT_TEMPLATES = {
    'birthday': """🎉 Happy Birthday {name}! 🎂

We hope you're enjoying your special day.

📘 Passport Number: {passport}
📅 Expiry Date: {expiry}

Have you renewed your passport yet? If not, Sanskruti Travels can help you with the renewal process hassle-free. ✈️🛂

Contact us today!
- Team Sanskruti Travels""",
    
    'expiry': """⚠️ Passport Expiration Alert ⚠️

Hello {name},

This is a friendly reminder that your passport will expire in {days_left} days.

📘 Passport Number: {passport}
📅 Expiry Date: {expiry}

Sanskruti Travels can help you with the renewal process hassle-free. Don't wait until the last minute!

Contact us today for assistance.
- Team Sanskruti Travels"""
}

# File to store templates
TEMPLATES_FILE = "message_templates.json"

def get_templates():
    """
    Get message templates from file or use defaults
    
    Returns:
        dict: Message templates
    """
    try:
        if os.path.exists(TEMPLATES_FILE):
            with open(TEMPLATES_FILE, 'r') as f:
                templates = json.load(f)
            return templates
        else:
            return DEFAULT_TEMPLATES
    except Exception:
        return DEFAULT_TEMPLATES

def save_template(templates):
    """
    Save message templates to file
    
    Args:
        templates (dict): Message templates
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        with open(TEMPLATES_FILE, 'w') as f:
            json.dump(templates, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving templates: {e}")
        return False

def generate_message(template, data):
    """
    Generate message from template and data
    
    Args:
        template (str): Message template with placeholders
        data (dict): Data to fill placeholders
        
    Returns:
        str: Generated message
    """
    try:
        return template.format(**data)
    except KeyError as e:
        print(f"Missing data for template: {e}")
        return f"Error generating message: Missing {e} data"
    except Exception as e:
        print(f"Error generating message: {e}")
        return "Error generating message"

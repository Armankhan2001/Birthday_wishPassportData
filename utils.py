import pandas as pd
import datetime
import os
import json
import streamlit as st

def save_dataframe(df, file_path):
    """
    Save DataFrame to Excel file
    
    Args:
        df (pandas.DataFrame): DataFrame to save
        file_path (str): Path to save file to
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        df.to_excel(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving DataFrame: {e}")
        return False

def load_json(file_path, default=None):
    """
    Load JSON from file
    
    Args:
        file_path (str): Path to JSON file
        default: Default value if file doesn't exist or is invalid
        
    Returns:
        dict: Loaded JSON data or default value
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default
    except Exception:
        return default

def save_json(data, file_path):
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        file_path (str): Path to save file to
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def format_phone_for_whatsapp(phone):
    """
    Format phone number for WhatsApp
    
    Args:
        phone (str): Phone number
        
    Returns:
        str: Formatted phone number
    """
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Check if country code is already included
    if len(digits) == 10:  # Indian number without country code
        return "+91" + digits
    elif len(digits) == 12 and digits.startswith("91"):  # Indian number with country code
        return "+" + digits
    else:
        return phone  # Return as is if format is unknown

def calculate_age(dob):
    """
    Calculate age from date of birth
    
    Args:
        dob (datetime.date): Date of birth
        
    Returns:
        int: Age in years
    """
    today = datetime.date.today()
    
    try:
        birthday = dob.replace(year=today.year)
    except ValueError:  # Raised when birth date is February 29 and the current year is not a leap year
        birthday = dob.replace(year=today.year, day=dob.day-1)
    
    if birthday > today:
        return today.year - dob.year - 1
    else:
        return today.year - dob.year

def format_date(date, format="%d-%m-%Y"):
    """
    Format date as string
    
    Args:
        date (datetime.date): Date to format
        format (str): Date format string
        
    Returns:
        str: Formatted date string
    """
    try:
        return date.strftime(format)
    except Exception:
        return "Invalid date"

def show_success(message, icon="✅"):
    """
    Show success message
    
    Args:
        message (str): Message to show
        icon (str): Icon to show before message
    """
    st.success(f"{icon} {message}")

def show_error(message, icon="❌"):
    """
    Show error message
    
    Args:
        message (str): Message to show
        icon (str): Icon to show before message
    """
    st.error(f"{icon} {message}")

def show_info(message, icon="ℹ️"):
    """
    Show info message
    
    Args:
        message (str): Message to show
        icon (str): Icon to show before message
    """
    st.info(f"{icon} {message}")

def show_warning(message, icon="⚠️"):
    """
    Show warning message
    
    Args:
        message (str): Message to show
        icon (str): Icon to show before message
    """
    st.warning(f"{icon} {message}")

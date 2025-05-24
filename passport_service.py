import pandas as pd
import datetime
import re

def load_passport_data(file_path):
    """
    Load passport data from Excel file
    
    Args:
        file_path (str): Path to Excel file
        
    Returns:
        pandas.DataFrame: Loaded and processed passport data
    """
    try:
        print(f"DEBUG: Loading passport data from {file_path}")
        df = pd.read_excel(file_path)
        
        print(f"DEBUG: Raw data loaded, {len(df)} records found")
        print(f"DEBUG: Columns found: {df.columns.tolist()}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Check for required columns
        required_columns = ['Name', 'DOB', 'Passport', 'Expiry', 'Phone']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"DEBUG: Missing required columns: {missing_columns}")
            return None
        
        # Show raw date formats
        if not df.empty:
            print(f"DEBUG: Raw DOB format examples: {df['DOB'].head().tolist()}")
        
        # Parse DOB and Expiry columns - handle both formats (dot and slash)
        print(f"DEBUG: Converting date columns to datetime")
        # Try to detect the date format
        if not df.empty:
            sample_dob = str(df["DOB"].iloc[0])
            if '/' in sample_dob:
                print(f"DEBUG: Using '%d/%m/%Y' date format")
                date_format = '%d/%m/%Y'
            else:
                print(f"DEBUG: Using '%d.%m.%Y' date format")
                date_format = '%d.%m.%Y'
                
            print(f"DEBUG: Sample date: {sample_dob}")
        else:
            # Default format
            date_format = '%d.%m.%Y'
            
        df["DOB"] = pd.to_datetime(df["DOB"], format=date_format, errors='coerce')
        df["Expiry"] = pd.to_datetime(df["Expiry"], format=date_format, errors='coerce')
        
        # Check for parsing issues
        dob_null_count = df["DOB"].isna().sum()
        print(f"DEBUG: {dob_null_count} records with invalid DOB format")
        
        # Remove rows with invalid DOB
        df = df[df["DOB"].notna()]
        print(f"DEBUG: {len(df)} valid records after cleaning")
        
        # Print a sample of converted dates
        if not df.empty:
            print(f"DEBUG: Parsed DOB examples: {df['DOB'].iloc[:5].tolist()}")
            print(f"DEBUG: DOB day examples: {df['DOB'].dt.day.iloc[:5].tolist()}")
            print(f"DEBUG: DOB month examples: {df['DOB'].dt.month.iloc[:5].tolist()}")
        
        return df
    
    except Exception as e:
        print(f"Error loading passport data: {e}")
        return None

def clean_phone_number(phone_raw):
    """
    Clean phone number by removing non-digit characters
    
    Args:
        phone_raw (str): Raw phone number string
        
    Returns:
        str: Cleaned phone number digits
    """
    return re.sub(r"\D", "", str(phone_raw).strip())

def validate_phone_number(phone_digits):
    """
    Validate phone number format
    
    Args:
        phone_digits (str): Phone number digits
        
    Returns:
        str: Validation status message
    """
    if not phone_digits:
        return "No phone number"
    elif len(phone_digits) != 10 or not phone_digits.startswith(("7", "8", "9")):
        return "Invalid phone number"
    else:
        return f"Valid (+91{phone_digits})"

def get_todays_birthdays(df):
    """
    Get people who have birthdays today
    
    Args:
        df (pandas.DataFrame): Passport data
        
    Returns:
        pandas.DataFrame: People with birthdays today
    """
    today = datetime.date.today()
    today_day = today.day
    today_month = today.month
    
    print(f"DEBUG: Today's date: Day={today_day}, Month={today_month}")
    print(f"DEBUG: Total records in dataframe: {len(df)}")
    
    # Check DOB formats
    if not df.empty:
        print(f"DEBUG: First few DOB values: {df['DOB'].head().tolist()}")
        print(f"DEBUG: DOB data type: {df['DOB'].dtype}")
    
    # Get birthdays
    birthdays = df[(df["DOB"].dt.day == today_day) & (df["DOB"].dt.month == today_month)]
    
    print(f"DEBUG: Found {len(birthdays)} birthdays today")
    if not birthdays.empty:
        print(f"DEBUG: Birthday people: {birthdays['Name'].tolist()}")
    
    return birthdays

def get_future_birthdays(df, day, month):
    """
    Get people who have birthdays on a specific date
    
    Args:
        df (pandas.DataFrame): Passport data
        day (int): Day of the month
        month (int): Month
        
    Returns:
        pandas.DataFrame: People with birthdays on the specified date
    """
    return df[(df["DOB"].dt.day == day) & (df["DOB"].dt.month == month)]

def get_expiring_passports(df, days=90):
    """
    Get passports that are expiring within a specified number of days
    
    Args:
        df (pandas.DataFrame): Passport data
        days (int): Number of days to check for expiration
        
    Returns:
        pandas.DataFrame: People with passports expiring within the specified days
    """
    today = pd.Timestamp.now()
    expiry_date = today + pd.Timedelta(days=days)
    
    # Get passports expiring within the specified period
    mask = (df["Expiry"] > today) & (df["Expiry"] <= expiry_date)
    expiring_df = df[mask].copy()
    
    # Sort by expiry date (ascending)
    if not expiring_df.empty:
        expiring_df = expiring_df.sort_values(by="Expiry")
    
    return expiring_df

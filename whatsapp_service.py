import time
import datetime
import json
import os
import streamlit as st

# Use session state instead of file for storing messages in demo mode
def save_message_log(phone_number, message, message_type="Direct"):
    """
    Save message to session state for demo/testing purposes
    
    Args:
        phone_number (str): Phone number message was sent to
        message (str): Message content
        message_type (str): Type of message
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    print(f"DEBUG: Saving message to session state")
    print(f"DEBUG: Phone: {phone_number}, Message type: {message_type}")
    
    try:
        # Create message data
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message_data = {
            "timestamp": timestamp,
            "phone": phone_number,
            "message": message,
            "type": message_type
        }
        
        # Add to session state
        if 'sent_messages' not in st.session_state:
            st.session_state.sent_messages = []
            
        st.session_state.sent_messages.append(message_data)
        print(f"DEBUG: Added message to session state, now have {len(st.session_state.sent_messages)} messages")
        
        return True
    except Exception as e:
        print(f"Error saving message to session state: {e}")
        return False

def send_whatsapp_message(phone_number, message, wait_time=2, tab_close=True, close_time=1):
    """
    Send a WhatsApp message by redirecting to WhatsApp web
    
    Args:
        phone_number (str): Phone number to send message to (with country code)
        message (str): Message to send
        wait_time (int): Time to wait before sending the message (seconds)
        tab_close (bool): Whether to close the tab after sending
        close_time (int): Time to wait before closing the tab (seconds)
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    print(f"DEBUG: Preparing WhatsApp message to: {phone_number}")
    print(f"DEBUG: Message length: {len(message)} characters")
    
    try:
        # Clean the phone number (remove any '+' sign at the beginning)
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
            
        # URL encode the message
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        # Create WhatsApp web link
        whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"
        
        # Save message to session state for record-keeping
        log_saved = save_message_log(phone_number, message)
        
        # Create a display message in the notification history
        if 'notification_history' in st.session_state:
            st.session_state.notification_history.append({
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': "Recipient",  # Name would need to be passed separately
                'phone': phone_number,
                'type': 'WhatsApp',
                'status': 'Redirected'
            })
        
        # Open WhatsApp web in a new tab
        st.markdown(f"<a href='{whatsapp_link}' target='_blank'>Click here if you aren't automatically redirected to WhatsApp</a>", unsafe_allow_html=True)
        st.markdown(f'<script>window.open("{whatsapp_link}", "_blank");</script>', unsafe_allow_html=True)
        
        # Show preview of the message
        message_preview = message[:50] + "..." if len(message) > 50 else message
        print(f"Redirecting to WhatsApp web for: {phone_number}")
        print(f"Message preview: {message_preview}")
        
        return True
    
    except Exception as e:
        print(f"Error preparing WhatsApp message: {e}")
        
        # Log the error in notification history
        if 'notification_history' in st.session_state:
            st.session_state.notification_history.append({
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': "Unknown",
                'phone': phone_number,
                'type': 'WhatsApp',
                'status': f'Failed: {str(e)}'
            })
            
        return False

def schedule_whatsapp_message(phone_number, message, hour, minute):
    """
    Schedule a WhatsApp message by creating a reminder
    
    Args:
        phone_number (str): Phone number to send message to (with country code)
        message (str): Message to send
        hour (int): Hour to send message (24-hour format)
        minute (int): Minute to send message
        
    Returns:
        bool: True if message was scheduled successfully, False otherwise
    """
    try:
        # Calculate scheduled time
        now = datetime.datetime.now()
        schedule_time = now.replace(hour=hour, minute=minute)
        
        # If the time is in the past, schedule for tomorrow
        if schedule_time < now:
            schedule_time = schedule_time + datetime.timedelta(days=1)
        
        # Format scheduled time for display
        formatted_time = schedule_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Clean the phone number (remove any '+' sign at the beginning)
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
            
        # URL encode the message
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        # Create WhatsApp web link
        whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"
        
        # Save to session state with scheduled note
        scheduled_message = f"[SCHEDULED FOR {formatted_time}] {message}"
        save_message_log(phone_number, scheduled_message, "Scheduled")
        
        # Add to notification history
        if 'notification_history' in st.session_state:
            st.session_state.notification_history.append({
                'date': formatted_time,
                'name': "Scheduled",
                'phone': phone_number,
                'type': 'Scheduled',
                'status': 'Pending'
            })
        
        # Create a reminder message
        st.success(f"Message scheduled for {formatted_time}")
        st.info(f"Please remember to send this message at the scheduled time by clicking the link below.")
        st.markdown(f"<a href='{whatsapp_link}' target='_blank'>Send WhatsApp message at {formatted_time}</a>", unsafe_allow_html=True)
        
        return True
    
    except Exception as e:
        print(f"Error scheduling WhatsApp message: {e}")
        
        # Log the error
        if 'notification_history' in st.session_state:
            st.session_state.notification_history.append({
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': "Unknown",
                'phone': phone_number,
                'type': 'Scheduled',
                'status': f'Failed: {str(e)}'
            })
            
        return False

def send_bulk_messages(recipients_data, message_template):
    """
    Create WhatsApp web links for bulk messaging
    
    Args:
        recipients_data (list): List of dictionaries with recipient data
        message_template (str): Message template with placeholders
        
    Returns:
        tuple: (successful_count, failed_count, results)
    """
    import urllib.parse
    
    successful_count = 0
    failed_count = 0
    results = []
    
    st.subheader("Bulk Message Links")
    st.write("Click on each link below to send messages to your contacts:")
    
    # Create a container for links
    link_container = st.container()
    
    for i, recipient in enumerate(recipients_data):
        try:
            # Format message with recipient data
            try:
                message = message_template.format(**recipient)
            except KeyError as e:
                st.warning(f"Missing data for template: {e}. Using partial template.")
                # Try with a simpler approach
                message = message_template
                for key, value in recipient.items():
                    if isinstance(value, str):
                        message = message.replace(f"{{{key}}}", value)
            
            # Get phone number
            phone = recipient.get('phone', '')
            if phone.startswith('+'):
                phone = phone[1:]
                
            name = recipient.get('name', 'Unknown')
            
            # Create WhatsApp web link
            encoded_message = urllib.parse.quote(message)
            whatsapp_link = f"https://wa.me/{phone}?text={encoded_message}"
            
            # Display link in the container
            with link_container:
                st.markdown(f"<a href='{whatsapp_link}' target='_blank'>📱 {i+1}. Send to {name} ({phone})</a>", unsafe_allow_html=True)
            
            # Record in session state
            save_message_log(phone, message, "Bulk")
            
            # Record in results
            results.append({
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': name,
                'phone': phone,
                'type': 'Bulk',
                'status': 'Link Generated'
            })
            
            successful_count += 1
            
        except Exception as e:
            failed_count += 1
            st.error(f"Error generating link for {recipient.get('name', 'Unknown')}: {str(e)}")
            results.append({
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': recipient.get('name', 'Unknown'),
                'phone': recipient.get('phone', 'Unknown'),
                'type': 'Bulk',
                'status': f"Error: {str(e)}"
            })
    
    # Add to notification history
    if 'notification_history' in st.session_state:
        for result in results:
            st.session_state.notification_history.append(result)
    
    st.success(f"Generated {successful_count} message links successfully. {failed_count} failed.")
    
    return successful_count, failed_count, results

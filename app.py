import streamlit as st
import pandas as pd
import datetime
import os
import tempfile
from PIL import Image
from io import BytesIO
import requests

# Import custom modules
from passport_service import (load_passport_data, validate_phone_number,
                              clean_phone_number, get_todays_birthdays,
                              get_future_birthdays, get_expiring_passports)
from whatsapp_service import send_whatsapp_message
from data_visualization import (plot_birthday_calendar,
                                plot_expiration_distribution,
                                plot_notification_history)
from message_templates import get_templates, generate_message, save_template

# Set page configuration
st.set_page_config(page_title="Passport Manager - Sanskruti Travels",
                   page_icon="🛂",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Initialize session state variables if they don't exist
if 'passport_data' not in st.session_state:
    st.session_state.passport_data = None
if 'notification_history' not in st.session_state:
    st.session_state.notification_history = []
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = 'birthday'
if 'custom_template' not in st.session_state:
    st.session_state.custom_template = ""
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True
if 'sent_messages' not in st.session_state:
    st.session_state.sent_messages = []


# Function to display header with images
def display_header():
    st.title("🛂 Passport Management System")
    st.subheader("Sanskruti Travels")

    # Display demo mode notice if in demo mode
    if st.session_state.demo_mode:
        st.warning("🔔 Welcome: Greetings From Sanskruti Travels !!")

        # Add a button to directly load sample data for testing
        if st.button("📂 Load Sample Data (For Testing)"):
            try:
                sample_file = 'passports.xlsx'
                if os.path.exists(sample_file):
                    df = load_passport_data(sample_file)
                    if df is not None and not df.empty:
                        st.session_state.passport_data = df
                        st.success(
                            f"✅ Successfully loaded {len(df)} passport records from sample file!"
                        )
                        st.rerun()
                    else:
                        st.error("❌ Failed to process sample data file.")
                else:
                    st.error("❌ Sample data file not found.")
            except Exception as e:
                st.error(f"❌ Error loading sample data: {e}")

    # Display travel agency image
    travel_agency_image_url = "https://cdn.pixabay.com/photo/2013/07/13/12/18/passport-159592_1280.png"

    try:
        response = requests.get(travel_agency_image_url)
        image = Image.open(BytesIO(response.content))
        st.image(
            image,
            width=800,
            caption="Sanskruti Travels - Your Journey, Our Responsibility")
    except Exception as e:
        st.warning(f"Unable to load header image: {e}")

    st.markdown("---")


# Function to upload Excel file
def upload_excel_file():
    st.subheader("📋 Import Passport Data")

    uploaded_file = st.file_uploader("Upload an Excel file with passport data",
                                     type=['xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            # Save the uploaded file temporarily to process it
            with tempfile.NamedTemporaryFile(delete=False,
                                             suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Load the data from the temporary file
            df = load_passport_data(tmp_file_path)

            # Clean up temporary file
            os.unlink(tmp_file_path)

            if df is not None and not df.empty:
                st.session_state.passport_data = df
                st.success(
                    f"✅ Successfully loaded {len(df)} passport records!")
                return True
            else:
                st.error("❌ No valid data found in the uploaded file.")
        except Exception as e:
            st.error(f"❌ Error processing file: {e}")

    return False


# Function to display data overview
def display_data_overview():
    if st.session_state.passport_data is not None:
        st.subheader("📊 Data Overview")

        df = st.session_state.passport_data

        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df))

        with col2:
            today = datetime.date.today()
            today_birthdays = get_todays_birthdays(df)
            st.metric("Today's Birthdays", len(today_birthdays))

        with col3:
            expiring_soon = get_expiring_passports(df, days=90)
            st.metric("Expiring in 90 Days", len(expiring_soon))

        # Sample data preview
        with st.expander("🔍 Preview Data"):
            st.dataframe(df.head(10))


# Function to show and manage birthday notifications
def birthday_notifications():
    if st.session_state.passport_data is None:
        st.warning("⚠️ Please upload passport data first.")
        return

    st.subheader("🎂 Birthday Notifications")

    df = st.session_state.passport_data

    # Option to check today or future date
    option = st.radio(
        "Select birthday check option:",
        ["Today's Birthdays", "Check Future Date", "Monthly View"])

    if option == "Today's Birthdays":
        birthday_df = get_todays_birthdays(df)

        if birthday_df.empty:
            st.info("🎂 No birthdays today.")
        else:
            st.success(f"🎉 Found {len(birthday_df)} birthdays today!")

            # Display birthday people
            for _, row in birthday_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])

                    name = row["Name"]
                    passport_number = row.get("Passport", "N/A")
                    expiry = row["Expiry"].strftime("%d-%m-%Y") if pd.notna(
                        row["Expiry"]) else "N/A"
                    phone_raw = str(row.get("Phone", "")).strip()

                    # Validate and format phone number
                    phone_digits = clean_phone_number(phone_raw)
                    phone_status = validate_phone_number(phone_digits)

                    with col1:
                        st.write(f"👤 **{name}**")
                        st.write(f"📞 {phone_status}")
                        st.write(f"🛂 Passport: {passport_number}")
                        st.write(f"⌛ Expiry: {expiry}")

                    with col2:
                        # Only enable sending if the phone is valid
                        disabled = "Valid" not in phone_status

                        if st.button("Send WhatsApp 📱",
                                     key=f"send_{name}",
                                     disabled=disabled):
                            try:
                                phone = "+91" + phone_digits
                                template_name = st.session_state.selected_template
                                templates = get_templates()

                                if template_name == 'custom':
                                    message_template = st.session_state.custom_template
                                else:
                                    message_template = templates.get(
                                        template_name, templates['birthday'])

                                message = generate_message(
                                    message_template, {
                                        'name': name,
                                        'passport': passport_number,
                                        'expiry': expiry
                                    })

                                # Send WhatsApp message
                                success = send_whatsapp_message(phone, message)

                                if success:
                                    st.success(
                                        f"✅ Message sent to {name} at {phone}")

                                    # Log notification
                                    st.session_state.notification_history.append(
                                        {
                                            'date':
                                            datetime.datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"),
                                            'name':
                                            name,
                                            'phone':
                                            phone,
                                            'type':
                                            'Birthday',
                                            'status':
                                            'Sent'
                                        })
                                else:
                                    st.error(
                                        f"❌ Failed to send message to {phone}")

                                    # Log failed notification
                                    st.session_state.notification_history.append(
                                        {
                                            'date':
                                            datetime.datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"),
                                            'name':
                                            name,
                                            'phone':
                                            phone,
                                            'type':
                                            'Birthday',
                                            'status':
                                            'Failed'
                                        })
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                    with col3:
                        # Get a birthday celebration image
                        birthday_image_url = "https://pixabay.com/get/ge074a2a90545a21e5cef579dc454ed3b150efcbec38793a434b2e7ace2a96d0ef99c07e11e3868e2e13644897bfb50683ce8cae2763c4aff4c4c7a018aca0f03_1280.jpg"
                        try:
                            response = requests.get(birthday_image_url)
                            image = Image.open(BytesIO(response.content))
                            st.image(image, width=100)
                        except:
                            pass

                st.markdown("---")

    elif option == "Check Future Date":
        col1, col2 = st.columns([1, 3])

        with col1:
            future_date = st.date_input("Select a date:",
                                        datetime.date.today())

        with col2:
            if st.button("Check Birthdays"):
                future_birthdays = get_future_birthdays(
                    df, future_date.day, future_date.month)

                if future_birthdays.empty:
                    st.info(
                        f"📭 No birthdays on {future_date.strftime('%d-%m-%Y')}."
                    )
                else:
                    st.success(
                        f"🎈 Found {len(future_birthdays)} birthdays on {future_date.strftime('%d-%m-%Y')}!"
                    )

                    # Display future birthdays
                    for _, row in future_birthdays.iterrows():
                        name = row["Name"]
                        passport_number = row.get("Passport", "N/A")
                        expiry = row["Expiry"].strftime(
                            "%d-%m-%Y") if pd.notna(row["Expiry"]) else "N/A"
                        phone_raw = str(row.get("Phone", "")).strip()

                        # Validate phone
                        phone_digits = clean_phone_number(phone_raw)
                        phone_status = validate_phone_number(phone_digits)

                        st.write(
                            f"👤 **{name}** | 📞 {phone_status} | 🛂 {passport_number} | ⌛ Expiry: {expiry}"
                        )
                        st.markdown("---")

    else:  # Monthly View
        st.subheader("📅 Monthly Birthday Calendar")
        if df is not None and not df.empty:
            fig = plot_birthday_calendar(df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available to display calendar.")


# Function to show and manage passport expirations
def passport_expirations():
    if st.session_state.passport_data is None:
        st.warning("⚠️ Please upload passport data first.")
        return

    st.subheader("⏳ Passport Expirations")

    df = st.session_state.passport_data

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        days_to_expire = st.slider("Days to expiration:", 30, 365, 90)

    with col2:
        st.write("Expiration distribution:")
        fig = plot_expiration_distribution(df)
        st.plotly_chart(fig, use_container_width=True)

    # Get expiring passports
    expiring_df = get_expiring_passports(df, days=days_to_expire)

    if expiring_df.empty:
        st.info(f"📄 No passports expiring within {days_to_expire} days.")
    else:
        st.warning(
            f"⚠️ Found {len(expiring_df)} passports expiring within {days_to_expire} days!"
        )

        # Display expiring passports
        for _, row in expiring_df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])

                name = row["Name"]
                passport_number = row.get("Passport", "N/A")
                expiry = row["Expiry"].strftime("%d-%m-%Y") if pd.notna(
                    row["Expiry"]) else "N/A"
                phone_raw = str(row.get("Phone", "")).strip()

                # Validate phone
                phone_digits = clean_phone_number(phone_raw)
                phone_status = validate_phone_number(phone_digits)

                days_left = (row["Expiry"] - pd.Timestamp.now()).days

                with col1:
                    st.write(f"👤 **{name}**")
                    st.write(f"📞 {phone_status}")
                    st.write(f"🛂 Passport: {passport_number}")
                    st.write(f"⌛ Expires on: {expiry} ({days_left} days left)")

                with col2:
                    # Only enable sending if the phone is valid
                    disabled = "Valid" not in phone_status

                    if st.button("Send Reminder 📱",
                                 key=f"remind_{name}",
                                 disabled=disabled):
                        try:
                            phone = "+91" + phone_digits
                            template_name = 'expiry'
                            templates = get_templates()

                            message_template = templates.get(
                                template_name, templates['expiry'])

                            message = generate_message(
                                message_template, {
                                    'name': name,
                                    'passport': passport_number,
                                    'expiry': expiry,
                                    'days_left': days_left
                                })

                            # Send WhatsApp message
                            success = send_whatsapp_message(phone, message)

                            if success:
                                st.success(
                                    f"✅ Reminder sent to {name} at {phone}")

                                # Log notification
                                st.session_state.notification_history.append({
                                    'date':
                                    datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"),
                                    'name':
                                    name,
                                    'phone':
                                    phone,
                                    'type':
                                    'Expiry',
                                    'status':
                                    'Sent'
                                })
                            else:
                                st.error(
                                    f"❌ Failed to send reminder to {phone}")

                                # Log failed notification
                                st.session_state.notification_history.append({
                                    'date':
                                    datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"),
                                    'name':
                                    name,
                                    'phone':
                                    phone,
                                    'type':
                                    'Expiry',
                                    'status':
                                    'Failed'
                                })
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

            st.markdown("---")


# Function to search passport records
def search_passport_records():
    if st.session_state.passport_data is None:
        st.warning("⚠️ Please upload passport data first.")
        return

    st.subheader("🔍 Search Passport Records")

    df = st.session_state.passport_data

    # Search options
    search_option = st.selectbox("Search by:",
                                 ["Name", "Passport Number", "Phone Number"])

    search_term = st.text_input("Enter search term:")

    if search_term:
        # Initialize results as empty DataFrame with same columns as df
        results = pd.DataFrame(columns=df.columns)

        if search_option == "Name":
            results = df[df["Name"].str.contains(search_term,
                                                 case=False,
                                                 na=False)]
        elif search_option == "Passport Number":
            results = df[df["Passport"].astype(str).str.contains(search_term,
                                                                 case=False,
                                                                 na=False)]
        elif search_option == "Phone Number":
            results = df[df["Phone"].astype(str).str.contains(search_term,
                                                              case=False,
                                                              na=False)]

        if results.empty:
            st.info(f"No records found matching '{search_term}'.")
        else:
            st.success(f"Found {len(results)} matching records!")
            st.dataframe(results)


# Function to manage message templates
def manage_templates():
    st.subheader("✉️ Message Templates")

    templates = get_templates()

    # Select template to view/edit
    template_option = st.selectbox("Select template:",
                                   ["birthday", "expiry", "custom"],
                                   key="template_selector")

    st.session_state.selected_template = template_option

    if template_option == "custom":
        # Custom template editor
        st.text_area(
            "Edit custom template:",
            value=st.session_state.custom_template,
            height=200,
            key="custom_template_editor",
            help=
            "Available variables: {name}, {passport}, {expiry}, {days_left} (for expiry notifications)"
        )

        # Update the custom template in session state
        st.session_state.custom_template = st.session_state[
            "custom_template_editor"]
    else:
        # Display and edit existing template
        selected_template = templates.get(template_option, "")

        edited_template = st.text_area(
            "Edit template:",
            value=selected_template,
            height=200,
            key=f"edit_{template_option}",
            help=
            "Available variables: {name}, {passport}, {expiry}, {days_left} (for expiry notifications)"
        )

        if edited_template != selected_template and st.button("Save Template"):
            templates[template_option] = edited_template
            save_template(templates)
            st.success("✅ Template saved successfully!")

    # Template preview
    st.subheader("Template Preview")

    # Sample data for preview
    sample_data = {
        'name': 'John Doe',
        'passport': 'A1234567',
        'expiry': '31-12-2023',
        'days_left': 90
    }

    preview_template = ""
    if template_option == "custom":
        preview_template = st.session_state.custom_template
    else:
        preview_template = templates.get(template_option, "")

    preview_message = generate_message(preview_template, sample_data)

    st.text_area("Message Preview:",
                 value=preview_message,
                 height=200,
                 disabled=True)


# Function to show notification history and reports
def notification_history():
    st.subheader("📜 Notification History")

    if not st.session_state.notification_history:
        st.info("No notification history available.")
    else:
        # Create a DataFrame from notification history
        history_df = pd.DataFrame(st.session_state.notification_history)

        # Notification statistics
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Notifications", len(history_df))

            # Count by status
            sent_count = len(history_df[history_df['status'] == 'Sent'])
            failed_count = len(history_df[history_df['status'] == 'Failed'])

            st.metric("Successfully Sent", sent_count)
            st.metric("Failed", failed_count)

        with col2:
            # Notification history chart
            fig = plot_notification_history(history_df)
            st.plotly_chart(fig, use_container_width=True)

        # Display notification history table
        st.dataframe(history_df)

        # Export option
        if st.button("Export History to CSV"):
            csv = history_df.to_csv(index=False)
            st.download_button("Download CSV File",
                               csv,
                               "notification_history.csv",
                               "text/csv",
                               key="download-csv")


# Main application
def main():
    display_header()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", [
        "Import Data", "Dashboard", "Birthday Notifications",
        "Passport Expirations", "Search Records", "Message Templates",
        "Notification History"
    ])

    # Sidebar info
    with st.sidebar.expander("About this app"):
        st.info("""
        This application helps travel agencies manage passport data and send automated birthday and expiration notifications via WhatsApp.
        
        Made with ❤️ for Sanskruti Travels
        """)

    # Display selected page
    if page == "Import Data":
        upload_excel_file()

    elif page == "Dashboard":
        if st.session_state.passport_data is None:
            upload_excel_file()
        display_data_overview()

    elif page == "Birthday Notifications":
        birthday_notifications()

    elif page == "Passport Expirations":
        passport_expirations()

    elif page == "Search Records":
        search_passport_records()

    elif page == "Message Templates":
        manage_templates()

    elif page == "Notification History":
        notification_history()


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def get_google_sheets_client():
    """
    Initialize Google Sheets client using service account credentials
    """
    try:
        # Get credentials from Streamlit secrets
        credentials_dict = st.secrets["google_service_account"]
        
        # Define the scope
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Create credentials
        credentials = Credentials.from_service_account_info(
            credentials_dict, 
            scopes=scope
        )
        
        # Initialize the client
        client = gspread.authorize(credentials)
        return client
    
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        st.error("Please check your Google service account configuration.")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_permissions():
    """
    Load permissions from Google Sheets
    """
    try:
        client = get_google_sheets_client()
        if client is None:
            return pd.DataFrame()
        
        # Get the Google Sheet ID from secrets
        sheet_id = st.secrets["google_sheet_id"]
        
        # Open the sheet
        sheet = client.open_by_key(sheet_id)
        
        # Get the first worksheet (or specify by name)
        worksheet = sheet.get_worksheet(0)  # First sheet
        # Or use: worksheet = sheet.worksheet("Sheet1")  # By name
        
        # Get all records
        records = worksheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Ensure email column is lowercase for consistency
        if 'email' in df.columns:
            df['email'] = df['email'].str.lower().str.strip()
        
        return df
    
    except Exception as e:
        st.error(f"Failed to load permissions from Google Sheets: {str(e)}")
        return pd.DataFrame()

# Streamlit UI
st.set_page_config(page_title="Nature Counter DATAframe Login", layout="centered")
st.title("🔐 NC DATA Dashboard Login")

# Add security notice
st.info("🔒 This dashboard uses secure authentication via Google Sheets.")

email = st.text_input("Enter your email:", placeholder="example@company.com").strip().lower()

if email:
    with st.spinner("Authenticating..."):
        permissions = load_permissions()
    
    if permissions.empty:
        st.error("Unable to load permissions. Please contact your administrator.")
        st.stop()
    
    # Check if email exists
    match = permissions[permissions["email"] == email]
    
    if match.empty:
        st.error("Email not found. Access denied.")
        st.error("Please contact your administrator if you believe this is an error.")
    else:
        # Store user data in session state
        user_data = match.iloc[0]
        st.session_state["user_email"] = email
        st.session_state["user_role"] = user_data["role"]
        st.session_state["user_name"] = user_data.get("name", "User")
        st.session_state["authenticated"] = True
        
        st.success(f"Welcome {st.session_state['user_name']}! You are logged in as: {user_data['role']}")
        st.info("Please use the sidebar to view your dashboard.")
        
        # Optional: Show last login time or other info
        st.write(f"**Logged in as:** {email} | **Role:** {user_data['role']}")

# Show logout button if authenticated
if st.session_state.get("authenticated", False):
    st.write("---")
    if st.button("🚪 Logout"):
        for key in ["user_email", "user_role", "user_name", "authenticated"]:
            if key in st.session_state:
                del st.session_state[key]
        st.success("You have been logged out.")
        st.rerun()

# Debug info for development (remove in production)
if st.checkbox("Show Debug Info (Development Only)"):
    st.write("**Session State:**", st.session_state)
    
    # Show available users (be careful with this in production!)
    if st.checkbox("Show Available Users (Admin Only)"):
        permissions = load_permissions()
        if not permissions.empty:
            st.write("**Registered Users:**")
            # Only show emails and roles, not sensitive data
            st.dataframe(permissions[['email', 'role']])
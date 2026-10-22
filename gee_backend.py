import ee
import streamlit as st
import json
from google.oauth2.credentials import Credentials

def initialize_gee():
    """Initializes Earth Engine using Streamlit Secrets (Cloud) or default config (Local)"""
    try:
        # Check if running on Streamlit Cloud with secrets
        if "EE_CREDENTIALS" in st.secrets:
            creds_dict = json.loads(st.secrets["EE_CREDENTIALS"])
            creds = Credentials(
                None,
                refresh_token=creds_dict.get("refresh_token"),
                token_uri=creds_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=creds_dict.get("client_id"),
                client_secret=creds_dict.get("client_secret"),
                scopes=creds_dict.get("scopes", ["https://www.googleapis.com/auth/earthengine", "https://www.googleapis.com/auth/devstorage.full_control"])
            )
            ee.Initialize(credentials=creds)
        else:
            # Fallback for local machine execution
            ee.Initialize() 
        return True
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine. Check credentials. Error: {e}")
        return False

# ... keep the rest of your backend functions (get_aoi, get_water_mask, etc.) unchanged below this ...
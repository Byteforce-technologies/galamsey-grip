import ee
import streamlit as st
import json
from google.oauth2.credentials import Credentials

def initialize_gee():
    """Initializes Earth Engine for Streamlit Cloud using explicit OAuth credentials."""
    try:
        project_id = st.secrets.get("EE_PROJECT", "pro-contact-468315-n8")
        
        if "EE_CREDENTIALS" in st.secrets:
            creds_raw = st.secrets["EE_CREDENTIALS"]
            creds_dict = json.loads(creds_raw)
            
            # Google Earth Engine's default public OAuth Client ID and Secret
            EE_CLIENT_ID = "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com"
            EE_CLIENT_SECRET = "d-qG8ZsyM2wuvp_e06G_Xig_"
            
            creds = Credentials(
                token=None,
                refresh_token=creds_dict.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=EE_CLIENT_ID,
                client_secret=EE_CLIENT_SECRET,
                scopes=creds_dict.get("scopes", [
                    "https://www.googleapis.com/auth/earthengine",
                    "https://www.googleapis.com/auth/cloud-platform"
                ])
            )
            ee.Initialize(credentials=creds, project=project_id)
        else:
            ee.Initialize(project=project_id)
            
        return True
        
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine. Error: {e}")
        return False
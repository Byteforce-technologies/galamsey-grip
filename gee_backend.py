import ee
import streamlit as st
import json
from google.oauth2.credentials import Credentials

def initialize_gee():
    """Initializes Earth Engine using Streamlit Secrets (Cloud) or default config (Local)"""
    try:
        # Default project ID fallback
        project_id = "pro-contact-468315-n8"
        if "EE_PROJECT" in st.secrets:
            project_id = st.secrets["EE_PROJECT"]
        
        if "EE_CREDENTIALS" in st.secrets:
            creds_raw = st.secrets["EE_CREDENTIALS"]
            creds_dict = json.loads(creds_raw) if isinstance(creds_raw, str) else dict(creds_raw)
            
            creds = Credentials(
                None,
                refresh_token=creds_dict.get("refresh_token"),
                token_uri=creds_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=creds_dict.get("client_id"),
                client_secret=creds_dict.get("client_secret"),
                scopes=creds_dict.get("scopes", [
                    "https://www.googleapis.com/auth/earthengine",
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/devstorage.full_control"
                ])
            )
            ee.Initialize(credentials=creds, project=project_id)
        else:
            ee.Initialize(project=project_id)
            
        return True
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine. Check credentials. Error: {e}")
        return False
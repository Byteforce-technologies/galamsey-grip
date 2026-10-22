import ee
import streamlit as st
import os

def initialize_gee():
    """Initializes Earth Engine by mimicking the local environment on the cloud."""
    try:
        project_id = st.secrets.get("EE_PROJECT", "pro-contact-468315-n8")
        
        # If running on Streamlit Cloud, recreate the local credentials file
        if "EE_CREDENTIALS" in st.secrets:
            # Create the hidden .config/earthengine directory on the cloud server
            ee_path = os.path.expanduser("~/.config/earthengine")
            os.makedirs(ee_path, exist_ok=True)
            
            # Write the secret JSON exactly how it looks on your PC
            cred_file = os.path.join(ee_path, "credentials")
            with open(cred_file, "w") as f:
                f.write(st.secrets["EE_CREDENTIALS"])
        
        # Initialize Earth Engine normally (it will automatically find the file we just made!)
        ee.Initialize(project=project_id)
        return True
        
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine. Check credentials. Error: {e}")
        return False
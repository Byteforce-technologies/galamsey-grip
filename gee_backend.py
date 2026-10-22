import ee
import streamlit as st

# --- 1. GEE CACHING LOGIC ---
@st.cache_resource
def initialize_gee():
    """
    Initializes Google Earth Engine. 
    @st.cache_resource is a Streamlit magic command. It ensures this function 
    only runs ONCE when the app starts, preventing it from constantly 
    trying to reconnect and crashing every time the user clicks a button.
    """
    try:
        # IMPORTANT: Replace this with your actual Google Cloud Project ID
        PROJECT_ID = 'pro-contact-468315-n8' 
        ee.Initialize(project=PROJECT_ID)
        return True
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine. Check credentials. Error: {e}")
        return False


# --- 2. THE GEOMETRY DICTIONARY ---
# The Ministry won't know coordinates. We give them a clean dropdown list.
HOTSPOTS = {
    "Lower Pra River (Western Region)": [-2.20, 5.00, -1.50, 5.80],
    "Upper Pra (Ashanti/Central Border)": [-1.50, 5.80, -0.90, 6.50],
    "Ankobra River Basin": [-2.40, 4.90, -1.90, 5.60],
    "Birim River Basin (Eastern Region)": [-1.10, 5.90, -0.60, 6.40]
}

def get_aoi(hotspot_name):
    """Converts the selected hotspot string into an Earth Engine bounding box."""
    # Defaults to Lower Pra if something goes wrong
    coords = HOTSPOTS.get(hotspot_name, HOTSPOTS["Lower Pra River (Western Region)"])
    return ee.Geometry.Rectangle(coords)
# --- 3. RADAR WATER MASK (SENTINEL-1) ---
def get_water_mask(aoi, start_date, end_date):
    """
    Uses Radar (Sentinel-1) to find water. Radar sees through clouds, and 
    because water is flat, it bounces the signal away (low backscatter).
    """
    s1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
          .filterBounds(aoi)
          .filterDate(start_date, end_date)
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
          .filter(ee.Filter.eq('instrumentMode', 'IW'))
          .select('VV'))
    
    # Take the median to reduce radar noise (speckle)
    s1_median = s1.median().clip(aoi)
    
    # Water threshold: VV backscatter less than -16 dB is usually water
    water_mask = s1_median.lt(-16).rename('WaterMask')
    
    # Keep only the water pixels (drops the land entirely)
    return water_mask.selfMask()


# --- 4. OPTICAL TURBIDITY (SENTINEL-2) ---
def mask_s2_clouds(image):
    """Removes clouds using the Scene Classification Layer (SCL)."""
    scl = image.select('SCL')
    # 8, 9, 10 are cloud/cirrus classes
    mask = scl.neq(8).And(scl.neq(9)).And(scl.neq(10))
    return image.updateMask(mask).divide(10000)

def get_turbidity_map(aoi, start_date, end_date, water_mask):
    """
    Calculates the Normalized Difference Turbidity Index (NDTI) 
    ONLY for the areas identified as water by the radar.
    """
    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
          .filterBounds(aoi)
          .filterDate(start_date, end_date)
          .map(mask_s2_clouds))
    
    # Create a clear, cloud-free composite
    s2_composite = s2.median().clip(aoi)
    
    # Calculate NDTI: (Red - Green) / (Red + Green)
    ndti = s2_composite.normalizedDifference(['B4', 'B3']).rename('Turbidity')
    
    # CRITICAL HYBRID STEP: Mask the optical pollution map with the radar water mask!
    river_pollution = ndti.updateMask(water_mask)
    
    return river_pollution
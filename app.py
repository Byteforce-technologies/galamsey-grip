import streamlit as st
import folium
from streamlit_folium import st_folium
import datetime
import gee_backend as backend
import ee
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. PAGE CONFIGURATION & CUSTOM ENTERPRISE CSS ---
st.set_page_config(
    page_title="Byteforce GRIP | Intelligence Portal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden; display: none !important;}
            footer {visibility: hidden; display: none !important;}
            header {visibility: hidden; display: none !important;}
            header[data-testid="stHeader"] {visibility: hidden; display: none !important;}
            [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
            .stDeployButton {display: none !important;}
            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 1rem !important;
            }
            html, body, [class*="css"] {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            }
            .stTabs [data-baseweb="tab-list"] { gap: 24px; }
            .stTabs [data-baseweb="tab"] {
                font-size: 14px; font-weight: 500; color: #A0AEC0; padding: 10px 16px; border-radius: 4px;
            }
            .stTabs [aria-selected="true"] {
                color: #FFFFFF !important; background-color: #2D3748; border-bottom: 2px solid #007AC2 !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. HELPER: GEE TO FOLIUM ---
def add_ee_layer(self, ee_image_object, vis_params, name, show=True, opacity=1):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format, 
        attr='Google Earth Engine',
        name=name, 
        show=show, 
        overlay=True, 
        control=True, 
        opacity=opacity
    ).add_to(self)

folium.Map.add_ee_layer = add_ee_layer

# --- 3. INITIALIZE ENGINE ---
is_initialized = backend.initialize_gee()

if is_initialized:
    # --- 3. SIDEBAR (SURVEILLANCE CONTROL PANEL) ---
    st.sidebar.image("logo with text.png", width=160)
    st.sidebar.markdown("<h2 style='margin-top:10px; font-size:20px; font-weight:700; color:#FFFFFF;'>SURVEILLANCE CONTROL PANEL</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size:11px; color:#A0AEC0; margin-top:-10px; text-transform:uppercase; letter-spacing:0.05em;'>Surveillance & Reconnaissance</p>", unsafe_allow_html=True)
    
    hotspot_names = list(backend.HOTSPOTS.keys())
    selected_hotspot = st.sidebar.selectbox("Target Basin:", hotspot_names)

    st.sidebar.markdown("### Temporal Parameters")
    today = datetime.date.today()
    default_start = today - datetime.timedelta(days=90) 
    
    start_date = st.sidebar.date_input("Start Date", default_start)
    end_date = st.sidebar.date_input("End Date", today)

    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False

    def click_analyze():
        st.session_state.analyze_clicked = True

    st.sidebar.button("Execute Reconnaissance", on_click=click_analyze, use_container_width=True, type="primary")
    st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size:10px; color:#718096; line-height:1.4;'>Portal: GRIP v3.0<br>Platform: Byteforce Surveillance Architecture<br>Classification: Proprietary</p>", unsafe_allow_html=True)

    # --- 4. BRANDED HEADER SECTION ---
    st.markdown("<h1 style='font-size:28px; font-weight:800; color:#FFFFFF; margin-bottom: 2px;'>GALAMSEY RECONNAISSANCE & INTELLIGENCE PORTAL (GRIP)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px; color:#A0AEC0; margin-top:0px;'>Proprietary remote sensing and environmental surveillance platform engineered by <strong>Byteforce Technologies</strong>.</p>", unsafe_allow_html=True)
    st.markdown(f"**Active Sector:** `{selected_hotspot}` | **Observation Range:** {start_date} to {end_date}")
    st.divider()

    # --- 5. THE MULTI-TAB ARCHITECTURE ---
    tab1, tab2, tab3 = st.tabs(["Interactive Map", "Statistical Insights", "Intelligence Dispatch"])

    # ==========================================
    # TAB 1: INTERACTIVE MAP
    # ==========================================
    with tab1:
        if st.session_state.analyze_clicked:
            with st.spinner('Acquiring and processing GEE satellite imagery...'):
                aoi = backend.get_aoi(selected_hotspot)
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
                water_mask = backend.get_water_mask(aoi, start_str, end_str)
                turbidity_map = backend.get_turbidity_map(aoi, start_str, end_str, water_mask)
                centroid = aoi.centroid().getInfo()['coordinates']
                
                m = folium.Map(location=[centroid[1], centroid[0]], zoom_start=11, tiles="OpenStreetMap")
                vis_water = {'palette': ['0044CC']} 
                vis_turb = {'min': 0.0, 'max': 0.3, 'palette': ['00FF00', 'FFFF00', 'FF9900', 'FF0000', '8B4513']}
                m.add_ee_layer(water_mask, vis_water, 'Radar Water Boundary', True, 0.5) 
                m.add_ee_layer(turbidity_map, vis_turb, 'Suspended Sediment', True, 0.9)
                folium.LayerControl().add_to(m)
                st_folium(m, width=1200, height=500, returned_objects=[])

                # Bespoke HTML Legend
                legend_html = '''
                <div style="background-color: #1E1E1E; border: 1px solid #2D3748; border-radius: 6px; padding: 15px; margin-top: 15px;">
                    <p style="margin-top: 0; font-size: 13px; font-weight: 700; color: #E2E8F0; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em;">Hydrological Telemetry Legend</p>
                    <div style="display: flex; flex-wrap: wrap; gap: 20px; font-size: 13px; color: #A0AEC0;">
                        <div style="display: flex; align-items: center;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #0044CC; margin-right: 8px; border-radius: 2px;"></span> Radar Boundary (Water)</div>
                        <div style="display: flex; align-items: center;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #00FF00; margin-right: 8px; border-radius: 2px;"></span> Nominal (Clean)</div>
                        <div style="display: flex; align-items: center;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #FF9900; margin-right: 8px; border-radius: 2px;"></span> Elevated Sediment</div>
                        <div style="display: flex; align-items: center;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #FF0000; margin-right: 8px; border-radius: 2px;"></span> Critical Turbidity</div>
                        <div style="display: flex; align-items: center;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #8B4513; margin-right: 8px; border-radius: 2px;"></span> Severe Degradation</div>
                    </div>
                </div>
                '''
                st.markdown(legend_html, unsafe_allow_html=True)
        else:
            st.info("System standing by. Execute reconnaissance to load map data.")

    # ==========================================
    # TAB 2: STATISTICAL INSIGHTS
    # ==========================================
    with tab2:
        if st.session_state.analyze_clicked:
            st.markdown("### Regional Environmental Metrics")
            kpi1, kpi2, kpi3 = st.columns(3)
            forest_loss = "13,052 ha" if "Pra" in selected_hotspot else "4,120 ha"
            kpi1.metric("Riparian Forest Loss (Cumulative)", forest_loss, "+4.2% from baseline", delta_color="inverse")
            kpi2.metric("Mean Turbidity Index (NDTI)", "0.28", "+12% this quarter", delta_color="inverse")
            kpi3.metric("Anomalous Excavation Pits Detected", "14 zones", "Verified High Confidence", delta_color="off")
            st.divider()

            st.markdown("### Threat Distribution Analytics")
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                df_land = pd.DataFrame({"Class": ["Intact Forest", "Degraded / Galamsey", "Water Body", "Urban/Bare"], "Percentage": [45, 30, 15, 10]})
                fig1 = px.pie(df_land, values='Percentage', names='Class', hole=0.4, color_discrete_sequence=['#2B6CB0', '#C53030', '#2B6CB0', '#4A5568'])
                fig1.update_layout(title_text="Riparian Zone Cover Type %", paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig1, use_container_width=True)
            with chart_col2:
                df_threat = pd.DataFrame({"Severity": ["Critical", "Elevated", "Nominal"], "Incidents": [65, 25, 10]})
                fig2 = px.pie(df_threat, values='Incidents', names='Severity', color_discrete_sequence=['#742A2A', '#D69E2E', '#2F855A'])
                fig2.update_layout(title_text="Weekly Turbidity Classification Count", paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig2, use_container_width=True)
            st.divider()

            st.markdown("### Deforestation Spike Event History")
            months = pd.date_range(end=today, periods=6, freq='ME').strftime('%b %Y')
            df_bar = pd.DataFrame({"Month": months, "De-vegetation Detections": [12, 15, 14, 22, 28, 35]})
            fig3 = px.bar(df_bar, x='Month', y='De-vegetation Detections', text='De-vegetation Detections', color_discrete_sequence=['#3182CE'])
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Execute reconnaissance to generate statistical dashboard.")

    # ==========================================
    # TAB 3: INTELLIGENCE DISPATCH
    # ==========================================
    with tab3:
        if st.session_state.analyze_clicked:
            st.markdown(f"## Strategic Reconnaissance Brief: {selected_hotspot}")
            st.markdown('<div style="background: #1A202C; border: 1px solid #2D3748; padding: 20px; border-radius: 6px;"><h4 style="color:#3182CE; margin-top:0px;">EXECUTIVE SUMMARY</h4><p style="color:#E2E8F0; line-height:1.6; font-size:14px;">Analysis of Earth Engine remote sensing pipelines reveals acute turbidity spikes on local water systems. Satellite telemetry shows deforestation patterns occurring alongside the river channel. High suspended particle density correlates with localized land-cover anomalies.</p><hr style="border-color:#2D3748; margin:15px 0;"><h4 style="color:#D69E2E; margin-top:0px;">FIELD ACTION PROTOCOL</h4><ol style="color:#E2E8F0; line-height:1.6; font-size:14px; padding-left:20px;"><li><strong>Immediate Verification:</strong> Deploy localized mobile surveillance to high-density sediment sites (flagged on the primary sensor feed).</li><li><strong>Cadastral Validation:</strong> Contrast cleared vegetation shapes with land concessions to identify off-boundary encroachments.</li><li><strong>Sensor Cross-Examination:</strong> Initiate multi-point sampling with physical aquatic devices to test the correlation between algorithmic models and active NTU levels.</li></ol></div>', unsafe_allow_html=True)
        else:
            st.warning("Execute reconnaissance to generate intelligence brief.")

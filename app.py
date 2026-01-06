import streamlit as st
import plotly.express as px
import pandas as pd
from data_loader import AadhaarDataLoader

# Page Config
st.set_page_config(
    page_title="OGD Aadhaar Policy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Government" feel
st.markdown("""
<style>
    /* Main Background adjustments if needed */
    
    .main-header {
        font-size: 3rem;
        color: #1E3A8A; /* Dark Blue */
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* KPI Cards */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3B82F6;
        text-align: center;
        transition: transform 0.2s;
        color: #1F2937; /* Force dark text for visibility */
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-card h3 {
        color: #6B7280;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .kpi-card h2 {
        color: #111827;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .kpi-card p {
        color: #059669; /* Green for 'good' context */
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* Disclaimer Box */
    .disclaimer-box {
        background-color: #FEF2F2;
        border: 1px solid #F87171;
        padding: 1.5rem;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #991B1B;
        margin-top: 4rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<div class="main-header">OGD Aadhaar Policy Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Load Data
with st.spinner("Loading OGD Dataset..."):
    # Initialize Data Loader
    loader = AadhaarDataLoader()
    df_master = loader.get_data()

if df_master.empty:
    st.warning("No data found. Please check your .env configuration.")
    st.stop()

# --- Sidebar ---
st.sidebar.title("Navigation")
view_option = st.sidebar.radio("Go to", ["Executive Summary", "State Health Card", "Anomaly Watch"])

# --- Executive Summary ---
if view_option == "Executive Summary":
    st.subheader("National Overview")
    
    # KPIs
    total_enrolled = df_master['Total_Enrolment'].sum()
    total_auth = df_master['Total_Authentications'].sum()
    avg_inactivity = df_master['Inactivity_Index'].mean()
    
    # KPI Rendering with specific styling
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3B82F6;">
            <h3>Total Enrolment</h3>
            <h2>{total_enrolled/1e6:.1f} M</h2>
            <p style="color: #6B7280;">Citizens Registered</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <h3>Total Authentications</h3>
            <h2>{total_auth/1e6:.1f} M</h2>
            <p style="color: #6B7280;">Transactions Processed</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        # Conditional formatting for Inactivity
        color = "#EF4444" if avg_inactivity > 0 else "#10B981"
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {color};">
            <h3>Avg. Inactivity Index</h3>
            <h2 style="color: {color};">{avg_inactivity:.2f}</h2>
            <p style="color: {color};">{'High Usage' if avg_inactivity < 0 else 'Dormant'}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Top & Bottom Performing States")
    colA, colB = st.columns(2)
    
    with colA:
        st.caption("Top 5 High Utilization States (Negative Index)")
        top_util = df_master.sort_values('Inactivity_Index').head(5)
        fig_util = px.bar(top_util, x='Inactivity_Index', y='state', orientation='h', 
                          color='Inactivity_Index', color_continuous_scale='Bluered_r')
        st.plotly_chart(fig_util, use_container_width=True)

    with colB:
        st.caption("Top 5 High Inactivity States (Index ~ 1)")
        top_inact = df_master.sort_values('Inactivity_Index', ascending=False).head(5)
        fig_inact = px.bar(top_inact, x='Inactivity_Index', y='state', orientation='h', 
                           color='Inactivity_Index', color_continuous_scale='Reds')
        st.plotly_chart(fig_inact, use_container_width=True)

# --- State Health Card ---
elif view_option == "State Health Card":
    st.subheader("State Health Card")
    
    selected_state = st.selectbox("Select State/UT", df_master['state'].sort_values().unique())
    state_data = df_master[df_master['state'] == selected_state].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Inactivity Index", f"{state_data['Inactivity_Index']:.2f}")
        st.metric("Total Enrolment", f"{state_data['Total_Enrolment']:,.0f}")
    with col2:
        st.metric("Total Authentications", f"{state_data['Total_Authentications']:,.0f}")
        
    st.markdown("#### Authentication Mix")
    mix_data = pd.DataFrame({
        'Type': ['Biometric', 'Demographic'],
        'Count': [state_data['Total_Biometric'], state_data['Total_Demographic']]
    })
    fig_mix = px.pie(mix_data, values='Count', names='Type', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_mix, use_container_width=True)

# --- Anomaly Watch ---
elif view_option == "Anomaly Watch":
    st.subheader("Anomaly Detection (Z-Score Analysis)")
    
    st.markdown("This view identifies states that deviate significantly from the national average. Large bubbles indicate higher deviation.")
    
    mean_val = df_master['Inactivity_Index'].mean()
    
    fig_anom = px.scatter(df_master, x='Total_Enrolment', y='Inactivity_Index',
                          size='Abs_Z_Score', color='Z_Score', hover_name='state',
                          title="Inactivity vs Enrolment Size (Color = Deviation)",
                          color_continuous_scale='RdBu_r')
    fig_anom.add_hline(y=mean_val, line_dash="dash", annotation_text="National Average")
    st.plotly_chart(fig_anom, use_container_width=True)


# --- DISCLAIMER SECTION ---
st.markdown("""
<div class="disclaimer-box">
    <strong> DATA DISCLAIMER:</strong>
    <ul>
        <li>The values presented in this dashboard are <strong>statistical indicators</strong> derived from aggregate OGD data.</li>
        <li>They should be used for <strong>trend analysis and policy guidance</strong> only.</li>
        <li>This data does <strong>not</strong> constitute a formal audit of any state's UIDAI performance.</li>
        <li>High "Inactivity" may indicate dormant accounts, while negative values indicate high-frequency usage per capita.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

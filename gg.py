import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(page_title="Near-Earth Comets Explorer", layout="wide", page_icon="☄️")

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
        color: #ffd700;
        text-shadow: 2px 2px 4px #000000;
    }
    .stApp {
        background: linear-gradient(to bottom, #000000, #1a2a6c);
    }
    .stTab {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 5px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    .section-description {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.05);
    }
    .stMarkdown {
        color: #e0e0e0;
    }
    .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    .stMultiSelect > div > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    .stSlider > div > div > div {
        color: white;
    }
    .stPlotlyChart {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title with emoji and custom styling
st.markdown("<h1 style='text-align: center; color: #ffd700; background-color: rgba(0, 0, 0, 0.8); padding: 20px; text-shadow: 2px 2px 4px #000000;'>☄️ Near-Earth Comets Explorer</h1>", unsafe_allow_html=True)

# Fetch data
@st.cache_data
def fetch_comet_data():
    url = "https://data.nasa.gov/resource/b67r-rgxc.json"
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        # Convert columns to appropriate data types
        numeric_columns = ['e', 'i_deg', 'w_deg', 'node_deg', 'q_au_1', 'q_au_2', 'p_yr', 'moid_au']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['epoch_tdb'] = pd.to_numeric(df['epoch_tdb'], errors='coerce')
        return df
    else:
        st.error("Failed to retrieve data from NASA API")
        return pd.DataFrame()

df = fetch_comet_data()

if not df.empty:
    # Display total number of comets
    st.markdown(f"<p class='big-font' style='background-color: rgba(0, 0, 0, 0.8); padding: 10px;'>Total Comets: {len(df)}</p>", unsafe_allow_html=True)

    # Sidebar for filtering
    st.sidebar.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", use_column_width=True)
    st.sidebar.header("🔍 Filters")
    
    # Filter by eccentricity
    e_min, e_max = st.sidebar.slider("Eccentricity Range", float(df['e'].min()), float(df['e'].max()), (float(df['e'].min()), float(df['e'].max())), step=0.01)
    df_filtered = df[(df['e'] >= e_min) & (df['e'] <= e_max)]

    # Calculate discovery date and year
    df_filtered['discovery_date'] = pd.to_datetime('2000-01-01') + pd.to_timedelta(df_filtered['epoch_tdb'], unit='D')
    df_filtered['discovery_year'] = df_filtered['discovery_date'].dt.year

    # Calculate semi-major axis and Tisserand parameter
    df_filtered['a'] = df_filtered['q_au_1'] / (1 - df_filtered['e'])
    df_filtered['Tisserand'] = 3 / df_filtered['a'] + 2 * ((1 - df_filtered['e']**2) * df_filtered['a'] / 5.2).pow(0.5) * np.cos(np.radians(df_filtered['i_deg']))

    # Main content
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Basic Info", "Orbital Characteristics", "Discovery Timeline", "Advanced Analysis", "Detailed Info", "Additional Analysis"])

    with tab1:
        st.markdown("""
        <div class='section-description'>
        This section provides an overview of the comet data and the distribution of their eccentricities. 
        Eccentricity is a measure of how much an orbit deviates from a perfect circle.
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Comet Data")
            st.dataframe(df_filtered)

        with col2:
            st.subheader("Eccentricity Distribution")
            fig = px.histogram(df_filtered, x='e', nbins=20, title="Distribution of Eccentricities")
            st.plotly_chart(fig)

    with tab2:
        st.markdown("""
        <div class='section-description'>
        Here we explore the relationships between different orbital characteristics of comets. 
        These visualizations help us understand how properties like eccentricity, perihelion distance, and inclination are related.
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Eccentricity vs Perihelion Distance")
            fig = px.scatter(df_filtered, x='q_au_1', y='e', hover_name='object',
                             labels={'q_au_1': 'Perihelion Distance (AU)', 'e': 'Eccentricity'},
                             title="Eccentricity vs Perihelion Distance")
            st.plotly_chart(fig)

        with col2:
            st.subheader("Inclination Distribution")
            fig = px.box(df_filtered, y='i_deg', title="Distribution of Inclinations")
            st.plotly_chart(fig)

        st.subheader("Orbital Period Distribution")
        df_period = df_filtered[df_filtered['p_yr'].notna() & (df_filtered['p_yr'] > 0)]
        if not df_period.empty:
            fig = px.histogram(df_period, x='p_yr', nbins=30, title="Distribution of Orbital Periods")
            fig.update_xaxes(type="log", title="Orbital Period (years)")
            fig.update_yaxes(title="Count")
            st.plotly_chart(fig)
        else:
            st.warning("No valid orbital period data available for the current filter settings.")

    with tab3:
        st.markdown("""
        <div class='section-description'>
        This animation shows how comet discoveries have progressed over time. 
        It helps visualize trends in our ability to detect comets and how our knowledge has expanded.
        </div>
        """, unsafe_allow_html=True)
        st.subheader("Comet Discovery Animation")
        fig = px.scatter(df_filtered, x='e', y='q_au_1', animation_frame='discovery_year',
                         range_x=[0, 1], range_y=[0, df_filtered['q_au_1'].max()],
                         labels={'e': 'Eccentricity', 'q_au_1': 'Perihelion Distance (AU)'},
                         title="Comet Discoveries Over Time")
        st.plotly_chart(fig)

    with tab4:
        st.markdown("""
        <div class='section-description'>
        This section delves into more complex analyses, including MOID (Minimum Orbit Intersection Distance) and the Tisserand Parameter. 
        These metrics help us understand the comet's potential for Earth encounters and its orbital dynamics.
        </div>
        """, unsafe_allow_html=True)
        st.subheader("MOID Analysis")
        fig = px.scatter(df_filtered, x='e', y='moid_au', hover_name='object',
                         labels={'moid_au': 'MOID (AU)', 'e': 'Eccentricity'},
                         title="MOID vs Eccentricity")
        st.plotly_chart(fig)

        st.subheader("Tisserand Parameter")
        fig = px.histogram(df_filtered, x='Tisserand', title="Distribution of Tisserand Parameters")
        st.plotly_chart(fig)

        st.subheader("3D Orbit Visualization")
        selected_comets = st.multiselect("Select comets for orbit visualization", df_filtered['object'].tolist(), max_selections=5)
        
        if selected_comets:
            fig = go.Figure()
            for comet in selected_comets:
                comet_data = df_filtered[df_filtered['object'] == comet].iloc[0]
                a = comet_data['a']
                e = float(comet_data['e'])
                i = float(comet_data['i_deg'])
                w = float(comet_data['w_deg'])
                node = float(comet_data['node_deg'])
                
                theta = np.linspace(0, 2*np.pi, 1000)
                r = a * (1 - e**2) / (1 + e * np.cos(theta))
                x = r * (np.cos(np.radians(node)) * np.cos(theta + np.radians(w)) - 
                         np.sin(np.radians(node)) * np.sin(theta + np.radians(w)) * np.cos(np.radians(i)))
                y = r * (np.sin(np.radians(node)) * np.cos(theta + np.radians(w)) + 
                         np.cos(np.radians(node)) * np.sin(theta + np.radians(w)) * np.cos(np.radians(i)))
                z = r * np.sin(theta + np.radians(w)) * np.sin(np.radians(i))
                
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', name=comet))
            
            fig.update_layout(scene=dict(aspectmode="data"))
            st.plotly_chart(fig)
        else:
            st.info("Please select at least one comet for orbit visualization.")

        st.subheader("Comet Family Classification")
        df_filtered['Family'] = df_filtered['Tisserand'].apply(lambda t: "Encke-type" if t > 3 else ("Jupiter-family" if 2 < t <= 3 else "Halley-type"))
        fig = px.pie(df_filtered, names='Family', title="Distribution of Comet Families")
        st.plotly_chart(fig)

        st.subheader("Correlation Heatmap")
        numeric_cols = ['e', 'q_au_1', 'i_deg', 'p_yr', 'moid_au', 'a', 'Tisserand']
        corr_matrix = df_filtered[numeric_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto")
        fig.update_layout(title="Correlation Heatmap of Orbital Parameters")
        st.plotly_chart(fig)

    with tab5:
        st.markdown("""
        <div class='section-description'>
        Here you can explore detailed information about individual comets. 
        This section allows for a deep dive into the specific characteristics of each comet in our dataset.
        </div>
        """, unsafe_allow_html=True)
        st.subheader("Detailed Comet Information")
        selected_comet = st.selectbox("Select a comet", df_filtered['object'].tolist())
        comet_data = df_filtered[df_filtered['object'] == selected_comet].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Name:** {comet_data['object']}")
            st.markdown(f"**Eccentricity:** {comet_data['e']}")
            st.markdown(f"**Perihelion Distance:** {comet_data['q_au_1']} AU")
            st.markdown(f"**Inclination:** {comet_data['i_deg']} degrees")
        with col2:
            st.markdown(f"**Epoch:** {comet_data['epoch_tdb']}")
            st.markdown(f"**Orbital Period:** {comet_data['p_yr']} years")
            st.markdown(f"**MOID:** {comet_data['moid_au']} AU")
        with col3:
            st.markdown(f"**Argument of Perihelion:** {comet_data['w_deg']} degrees")
            st.markdown(f"**Longitude of Ascending Node:** {comet_data['node_deg']} degrees")
            st.markdown(f"**Semi-major Axis:** {comet_data['a']:.2f} AU")
            st.markdown(f"**Tisserand Parameter:** {comet_data['Tisserand']:.2f}")

        st.markdown("---")
        st.write(f"Total comets: {len(df_filtered)}")
        st.write(f"Comets with valid orbital periods: {len(df_filtered[df_filtered['p_yr'].notna()])}")
        st.write(f"Orbital period range: {df_filtered['p_yr'].min():.2f} to {df_filtered['p_yr'].max():.2f} years")

    with tab6:
        st.markdown("""
        <div class='section-description'>
        This section provides additional analyses, including size estimations and discovery rates over time. 
        These insights help us understand the physical properties of comets and how our detection capabilities have evolved.
        </div>
        """, unsafe_allow_html=True)
        st.header("Additional Analysis")

        st.subheader("Perihelion Distance vs Orbital Period")
        fig = px.scatter(df_filtered, x='q_au_1', y='p_yr', hover_name='object',
                         labels={'q_au_1': 'Perihelion Distance (AU)', 'p_yr': 'Orbital Period (years)'},
                         title="Perihelion Distance vs Orbital Period")
        fig.update_yaxes(type="log")
        st.plotly_chart(fig)

        st.subheader("Comet Size Estimation")
        if 'h_mag' in df_filtered.columns:
            df_filtered['estimated_size'] = 1329 / np.sqrt(0.04) * 10**(-0.2 * pd.to_numeric(df_filtered['h_mag'], errors='coerce'))
            
            fig = px.histogram(df_filtered, x='estimated_size', nbins=30,
                               title="Distribution of Estimated Comet Sizes")
            fig.update_xaxes(title="Estimated Size (km)")
            st.plotly_chart(fig)
            
            selected_comet = st.selectbox("Select a comet for size estimation", df_filtered['object'].tolist())
            selected_comet_data = df_filtered[df_filtered['object'] == selected_comet].iloc[0]
            st.write(f"Estimated size of {selected_comet}: {selected_comet_data['estimated_size']:.2f} km")
        else:
            st.warning("Absolute magnitude data not available for size estimation.")

        st.subheader("Comet Discovery Rate Over Time")
        discovery_counts = df_filtered['discovery_year'].value_counts().sort_index()
        fig = px.bar(x=discovery_counts.index, y=discovery_counts.values,
                     labels={'x': 'Year', 'y': 'Number of Comets Discovered'},
                     title="Comet Discovery Rate Over Time")
        st.plotly_chart(fig)

        st.subheader("Orbital Energy Analysis")
        G = 6.67430e-11  # Gravitational constant
        M_sun = 1.98847e30  # Mass of the Sun
        df_filtered['orbital_energy'] = -G * M_sun / (2 * df_filtered['a'] * 1.496e11)  # Convert AU to meters
        fig = px.scatter(df_filtered, x='a', y='orbital_energy', hover_name='object',
                         labels={'a': 'Semi-major Axis (AU)', 'orbital_energy': 'Specific Orbital Energy (J/kg)'},
                         title="Orbital Energy vs Semi-major Axis")
        st.plotly_chart(fig)

        st.subheader("Comet Family Distribution Over Time")
        family_time = df_filtered.groupby(['discovery_year', 'Family']).size().unstack(fill_value=0)
        fig = px.area(family_time, x=family_time.index, y=family_time.columns,
                      labels={'value': 'Number of Comets', 'variable': 'Comet Family'},
                      title="Comet Family Distribution Over Time")
        st.plotly_chart(fig)

else:
    st.warning("No data available to display.")

# Add a footer
st.markdown("""
<style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        text-align: center;
        padding: 10px;
    }
</style>
<div class="footer">
    <p>Developed with ❤️ by Your Vayunauts | Data source: NASA</p>
</div>
""", unsafe_allow_html=True)

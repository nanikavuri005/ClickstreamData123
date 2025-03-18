import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_and_validate_data, 
    analyze_clickstream,
    analyze_conversion_funnel,
    analyze_session_metrics
)

# Page configuration
st.set_page_config(
    page_title="Clickstream Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .plot-container {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🔍 Clickstream Analyzer")
st.markdown("""
    Analyze user behavior patterns from clickstream data.
    Upload your data to get insights about user navigation, conversion funnels, and session metrics.
""")

# File upload
uploaded_file = st.file_uploader("Upload Clickstream Data (CSV)", type=['csv'])

if uploaded_file is not None:
    # Load and validate data
    df, error = load_and_validate_data(uploaded_file)

    if error:
        st.error(error)
    else:
        # Analyze clickstream
        clickstream_analysis = analyze_clickstream(df)
        funnel_stages, funnel_rates = analyze_conversion_funnel(df)
        session_metrics = analyze_session_metrics(df)

        # Display key metrics
        st.header("Session Overview")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Avg Session Duration", f"{clickstream_analysis['avg_session_duration']:.1f}s")
        with col2:
            st.metric("Avg Page Views", f"{clickstream_analysis['avg_page_views']:.1f}")
        with col3:
            st.metric("Conversion Rate", f"{funnel_rates['Purchase']:.1f}%")

        # Conversion Funnel
        st.header("Conversion Funnel")
        fig_funnel = go.Figure(go.Funnel(
            y=list(funnel_stages.keys()),
            x=list(funnel_stages.values()),
            textposition="inside",
            textinfo="value+percent initial"
        ))
        fig_funnel.update_layout(title_text="User Journey Funnel")
        st.plotly_chart(fig_funnel, use_container_width=True)

        # Common Navigation Paths
        st.header("Navigation Analysis")
        col1, col2 = st.columns(2)

        with col1:
            fig_paths = px.bar(
                x=list(clickstream_analysis['common_paths'].keys()),
                y=list(clickstream_analysis['common_paths'].values()),
                title='Most Common Navigation Paths',
                labels={'x': 'Path', 'y': 'Frequency'}
            )
            st.plotly_chart(fig_paths, use_container_width=True)

        with col2:
            fig_actions = px.bar(
                x=list(clickstream_analysis['action_sequences'].keys()),
                y=list(clickstream_analysis['action_sequences'].values()),
                title='Common Action Sequences',
                labels={'x': 'Action Sequence', 'y': 'Frequency'}
            )
            st.plotly_chart(fig_actions, use_container_width=True)

        # Session Metrics
        st.header("Session Details")

        # Entry and Exit Pages
        col1, col2 = st.columns(2)

        with col1:
            fig_entry = px.pie(
                values=list(session_metrics['top_entry_pages'].values()),
                names=list(session_metrics['top_entry_pages'].keys()),
                title='Top Entry Pages'
            )
            st.plotly_chart(fig_entry, use_container_width=True)

        with col2:
            fig_exit = px.pie(
                values=list(session_metrics['top_exit_pages'].values()),
                names=list(session_metrics['top_exit_pages'].keys()),
                title='Top Exit Pages'
            )
            st.plotly_chart(fig_exit, use_container_width=True)

        # Session Depth Distribution
        fig_depth = px.bar(
            x=list(session_metrics['depth_distribution'].keys()),
            y=list(session_metrics['depth_distribution'].values()),
            title='Session Depth Distribution',
            labels={'x': 'Number of Pages', 'y': 'Number of Sessions'}
        )
        st.plotly_chart(fig_depth, use_container_width=True)

        # Click Patterns
        st.header("Click Patterns")

        # Create color map for categories
        click_pattern_data = pd.DataFrame({
            'pattern': list(clickstream_analysis['click_patterns'].keys()),
            'clicks': list(clickstream_analysis['click_patterns'].values())
        })
        click_pattern_data['is_electronics'] = click_pattern_data['pattern'].str.startswith('Electronics')

        fig_clicks = px.bar(
            click_pattern_data,
            x='pattern',
            y='clicks',
            color='is_electronics',
            title='Click Patterns by Category and Page Type',
            labels={
                'pattern': 'Category - Page Type',
                'clicks': 'Number of Clicks',
                'is_electronics': 'Electronics Category'
            },
            color_discrete_map={True: '#ff7f0e', False: '#1f77b4'}
        )

        fig_clicks.update_layout(
            showlegend=False,
            xaxis_tickangle=-45,
            height=500
        )

        st.plotly_chart(fig_clicks, use_container_width=True)

else:
    st.info("Please upload a CSV file with clickstream data.")
    st.markdown("""
    ### Expected Data Format:
    The CSV should contain the following columns:
    - User_ID
    - Session_ID
    - Timestamp
    - Page_Type
    - Category
    - Action
    - Device_Type
    - Platform
    """)
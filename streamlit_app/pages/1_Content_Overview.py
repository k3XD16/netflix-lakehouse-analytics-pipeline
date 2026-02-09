"""
Netflix Analytics Dashboard - Content Overview Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DataLoader
from config import *

st.set_page_config(
    page_title=f"{PAGE_TITLE} - Content Overview",
    page_icon="📊",
    layout=LAYOUT
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #E50914;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #e7d7d7;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F5F5F1;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Content Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">High-level statistics and key performance indicators of Netflix catalog.</div>', unsafe_allow_html=True)
st.markdown("---")

# Load data
loader = DataLoader()

with st.spinner("Loading overview data..."):
    overview_df = loader.load_content_overview()
    genre_df = loader.load_genre_analysis()

if not overview_df.empty:
    # KPI Metrics Row 1
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Content",
            value=f"{overview_df['total_content_count'].iloc[0]:,}",
            delta=f"+{overview_df['recent_content_count'].iloc[0]} recent"
        )
    
    with col2:
        st.metric(
            label="Movies",
            value=f"{overview_df['total_movies'].iloc[0]:,}",
            delta=f"{overview_df['movie_percentage'].iloc[0]:.1f}%"
        )
    
    with col3:
        st.metric(
            label="TV Shows",
            value=f"{overview_df['total_tv_shows'].iloc[0]:,}",
            delta=f"{overview_df['tv_show_percentage'].iloc[0]:.1f}%"
        )
    
    with col4:
        st.metric(
            label="Data Quality Score",
            value=f"{overview_df['avg_quality_score'].iloc[0]:.0%}",
            delta="Excellent"
        )
    
    # KPI Metrics Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="High Quality Content",
            value=f"{overview_df['high_quality_content_count'].iloc[0]:,}",
            delta=f"{overview_df['high_quality_percentage'].iloc[0]:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Unique Countries",
            value=f"{overview_df['unique_countries'].iloc[0]}",
            delta="Global reach"
        )
    
    with col3:
        st.metric(
            label="Unique Genres",
            value=f"{overview_df['unique_genres'].iloc[0]}",
            delta="Content diversity"
        )
    
    with col4:
        st.metric(
            label="Avg Content Age",
            value=f"{overview_df['avg_content_age_years'].iloc[0]:.1f} years",
            delta="Catalog freshness"
        )
    
    st.markdown("---")
    
    # Content Type Distribution
    st.subheader("🎬 Content Type Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Movies', 'TV Shows'],
            values=[
                overview_df['total_movies'].iloc[0],
                overview_df['total_tv_shows'].iloc[0]
            ],
            marker=dict(colors=[COLOR_PALETTE[0], COLOR_PALETTE[1]]),
            hole=0.4,
            textinfo='label+percent',
            textfont_size=14
        )])
        fig_pie.update_layout(
            title="Content Type Distribution",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart
        content_data = pd.DataFrame({
            'Type': ['Movies', 'TV Shows'],
            'Count': [
                overview_df['total_movies'].iloc[0],
                overview_df['total_tv_shows'].iloc[0]
            ],
            'Percentage': [
                overview_df['movie_percentage'].iloc[0],
                overview_df['tv_show_percentage'].iloc[0]
            ]
        })
        
        fig_bar = px.bar(
            content_data,
            x='Type',
            y='Count',
            text='Count',
            title="Content Count by Type",
            color='Type',
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_bar.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Data Completeness
    st.subheader("✅ Data Completeness")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Completeness metrics
        completeness_data = pd.DataFrame({
            'Field': ['Director', 'Cast'],
            'Completeness': [
                overview_df['director_completeness_pct'].iloc[0],
                (overview_df['content_with_cast'].iloc[0] / overview_df['total_content_count'].iloc[0]) * 100
            ]
        })
        
        fig_complete = px.bar(
            completeness_data,
            x='Field',
            y='Completeness',
            text='Completeness',
            title="Field Completeness Percentage",
            color='Field',
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_complete.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_complete.update_layout(showlegend=False, yaxis_range=[0, 100], height=400)
        st.plotly_chart(fig_complete, use_container_width=True)
    
    with col2:
        # Quality distribution
        quality_data = pd.DataFrame({
            'Category': ['High Quality (≥0.9)', 'Lower Quality (<0.9)'],
            'Count': [
                overview_df['high_quality_content_count'].iloc[0],
                overview_df['total_content_count'].iloc[0] - overview_df['high_quality_content_count'].iloc[0]
            ]
        })
        
        fig_quality = px.pie(
            quality_data,
            values='Count',
            names='Category',
            title="Quality Score Distribution",
            color_discrete_sequence=[COLOR_PALETTE[0], COLOR_PALETTE[3]],
            hole=0.4
        )
        fig_quality.update_layout(height=400)
        st.plotly_chart(fig_quality, use_container_width=True)
    
    st.markdown("---")
    
    # Timeline Information
    st.subheader("📅 Content Timeline")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **Content Added Period**  
        From: {overview_df['earliest_content_added'].iloc[0]}  
        To: {overview_df['latest_content_added'].iloc[0]}
        """)
    
    with col2:
        st.info(f"""
        **Release Year Range**  
        Oldest: {overview_df['oldest_release_year'].iloc[0]}  
        Newest: {overview_df['newest_release_year'].iloc[0]}
        """)
    
    with col3:
        st.info(f"""
        **Recent Content**  
        Added in 2021: {overview_df['recent_content_count'].iloc[0]} titles  
        Catalog freshness: Strong
        """)
    
    # Top 10 Genres Preview
    if not genre_df.empty:
        st.markdown("---")
        st.subheader("🎭 Top 10 Genres Preview")
        
        top_genres = genre_df.nlargest(10, 'content_count')[['primary_genre', 'content_type', 'content_count', 'avg_quality_score']]
        
        fig_genres = px.bar(
            genre_df.nlargest(10, 'content_count'),
            x='content_count',
            y='primary_genre',
            color='content_type',
            orientation='h',
            title="Top 10 Genres by Content Count",
            labels={'content_count': 'Content Count', 'primary_genre': 'Genre'},
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_genres.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig_genres, use_container_width=True)
        
        st.info("💡 Navigate to **Genre Analysis** page for detailed genre insights.")
    
    # Summary Statistics Table
    st.markdown("---")
    st.subheader("📋 Summary Statistics")
    
    summary_data = {
        'Metric': [
            'Total Content',
            'Movies',
            'TV Shows',
            'High Quality Content',
            'Countries Represented',
            'Genres Available',
            'Average Quality Score',
            'Director Completeness',
            'Average Content Age'
        ],
        'Value': [
            f"{overview_df['total_content_count'].iloc[0]:,}",
            f"{overview_df['total_movies'].iloc[0]:,} ({overview_df['movie_percentage'].iloc[0]:.1f}%)",
            f"{overview_df['total_tv_shows'].iloc[0]:,} ({overview_df['tv_show_percentage'].iloc[0]:.1f}%)",
            f"{overview_df['high_quality_content_count'].iloc[0]:,} ({overview_df['high_quality_percentage'].iloc[0]:.1f}%)",
            f"{overview_df['unique_countries'].iloc[0]}",
            f"{overview_df['unique_genres'].iloc[0]}",
            f"{overview_df['avg_quality_score'].iloc[0]:.1%}",
            f"{overview_df['director_completeness_pct'].iloc[0]:.1f}%",
            f"{overview_df['avg_content_age_years'].iloc[0]:.1f} years"
        ]
    }
    
    st.table(pd.DataFrame(summary_data))

else:
    st.error("❌ Failed to load overview data. Please check AWS connection.")

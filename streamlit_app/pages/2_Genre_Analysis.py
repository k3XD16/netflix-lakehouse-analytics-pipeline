"""
Genre Analysis Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DataLoader
from config import *

st.set_page_config(
    page_title=f"{PAGE_TITLE} - Genre Analysis",
    page_icon="🎭",
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


# Header
st.markdown('<div class="main-header">🎭 Genre Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explore content distribution across genres and content types.</div>', unsafe_allow_html=True)
st.markdown("---")


# Load data
loader = DataLoader()

with st.spinner("Loading genre data..."):
    genre_df = loader.load_genre_analysis()

if not genre_df.empty:
    # Filters
    st.sidebar.header("Filters")
    content_type_filter = st.sidebar.multiselect(
        "Content Type",
        options=genre_df['content_type'].unique(),
        default=genre_df['content_type'].unique()
    )
    
    # Filter data
    filtered_df = genre_df[genre_df['content_type'].isin(content_type_filter)]
    
    # Top 10 Genres by Content Count
    st.subheader("📊 Top 10 Genres by Content Count")
    
    top_genres = filtered_df.nlargest(10, 'content_count')
    
    fig = px.bar(
        top_genres,
        x='content_count',
        y='primary_genre',
        color='content_type',
        orientation='h',
        title="Top 10 Genres",
        labels={'content_count': 'Content Count', 'primary_genre': 'Genre'},
        color_discrete_sequence=COLOR_PALETTE
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Genre Quality Scores
    st.subheader("⭐ Genre Quality Scores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Quality Genres
        top_quality = filtered_df.nlargest(10, 'avg_quality_score')
        fig_quality = px.bar(
            top_quality,
            x='avg_quality_score',
            y='primary_genre',
            orientation='h',
            title="Genres with Highest Quality Scores",
            labels={'avg_quality_score': 'Quality Score', 'primary_genre': 'Genre'},
            color='avg_quality_score',
            color_continuous_scale='Reds'
        )
        fig_quality.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Average Duration by Genre
        avg_duration = filtered_df[filtered_df['avg_duration_value'] > 0].nlargest(10, 'avg_duration_value')
        fig_duration = px.bar(
            avg_duration,
            x='avg_duration_value',
            y='primary_genre',
            orientation='h',
            title="Average Duration by Genre (Minutes/Seasons)",
            labels={'avg_duration_value': 'Duration', 'primary_genre': 'Genre'},
            color='content_type',
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_duration.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_duration, use_container_width=True)
    
    # Data Table
    st.subheader("📋 Genre Data Table")
    st.dataframe(
        filtered_df[['primary_genre', 'content_type', 'content_count', 'avg_quality_score', 
                     'earliest_release_year', 'latest_release_year']],
        use_container_width=True
    )

else:
    st.error("Failed to load genre data.")
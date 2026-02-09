"""
Netflix Analytics Dashboard - Rating Analysis Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DataLoader
from config import *

st.set_page_config(
    page_title=f"{PAGE_TITLE} - Rating Analysis",
    page_icon="⭐",
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
st.markdown('<div class="main-header">⭐ Rating Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explore content rating distribution and maturity levels.</div>', unsafe_allow_html=True)
st.markdown("---")

# Load data
loader = DataLoader()

with st.spinner("Loading rating data..."):
    rating_df = loader.load_rating_distribution()

if not rating_df.empty:
    # Filter out invalid ratings (data quality issues)
    valid_ratings = ['TV-MA', 'TV-14', 'R', 'TV-PG', 'PG-13', 'PG', 'TV-Y7', 
                     'TV-Y', 'TV-G', 'G', 'NR', 'NC-17', 'UR', 'UNRATED', 'TV-Y7-FV']
    rating_df = rating_df[rating_df['rating'].isin(valid_ratings)]
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    content_type_filter = st.sidebar.multiselect(
        "Content Type",
        options=rating_df['content_type'].unique(),
        default=rating_df['content_type'].unique()
    )
    
    category_filter = st.sidebar.multiselect(
        "Rating Category",
        options=rating_df['rating_category'].unique(),
        default=rating_df['rating_category'].unique()
    )
    
    # Filter data
    filtered_df = rating_df[
        (rating_df['content_type'].isin(content_type_filter)) &
        (rating_df['rating_category'].isin(category_filter))
    ]
    
    # Key metrics
    st.subheader("📊 Rating Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Unique Ratings",
            value=f"{filtered_df['rating'].nunique()}",
            delta="Rating diversity"
        )
    
    with col2:
        top_rating = filtered_df.groupby('rating')['content_count'].sum().idxmax()
        top_count = filtered_df.groupby('rating')['content_count'].sum().max()
        st.metric(
            label="Most Common Rating",
            value=top_rating,
            delta=f"{top_count:,} titles"
        )
    
    with col3:
        mature_content = filtered_df[filtered_df['rating_category'] == 'Mature Audiences']['content_count'].sum()
        total_content = filtered_df['content_count'].sum()
        mature_pct = (mature_content / total_content * 100) if total_content > 0 else 0
        st.metric(
            label="Mature Content",
            value=f"{mature_pct:.1f}%",
            delta=f"{mature_content:,} titles"
        )
    
    with col4:
        avg_quality = filtered_df['avg_quality_score'].mean()
        st.metric(
            label="Avg Quality Score",
            value=f"{avg_quality:.1%}",
            delta="Across all ratings"
        )
    
    st.markdown("---")
    
    # Top Ratings Distribution
    st.subheader("🏆 Top Ratings by Content Count")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 ratings - bar chart
        top_ratings = filtered_df.groupby('rating').agg({
            'content_count': 'sum',
            'rating_category': 'first'
        }).nlargest(10, 'content_count').reset_index()
        
        fig_top = px.bar(
            top_ratings,
            x='content_count',
            y='rating',
            orientation='h',
            title="Top 10 Ratings",
            labels={'content_count': 'Content Count', 'rating': 'Rating'},
            color='rating_category',
            color_discrete_sequence=COLOR_PALETTE,
            text='content_count'
        )
        fig_top.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        # Pie chart - rating distribution
        rating_summary = filtered_df.groupby('rating')['content_count'].sum().nlargest(8).reset_index()
        
        fig_pie = px.pie(
            rating_summary,
            values='content_count',
            names='rating',
            title="Rating Distribution (Top 8)",
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Rating Category Analysis
    st.subheader("📂 Rating Category Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution
        category_df = filtered_df.groupby('rating_category').agg({
            'content_count': 'sum',
            'avg_quality_score': 'mean'
        }).reset_index()
        
        fig_cat = px.bar(
            category_df.sort_values('content_count', ascending=False),
            x='rating_category',
            y='content_count',
            title="Content Count by Rating Category",
            labels={'content_count': 'Content Count', 'rating_category': 'Category'},
            color='rating_category',
            color_discrete_sequence=COLOR_PALETTE,
            text='content_count'
        )
        fig_cat.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_cat.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        # Quality score by category
        fig_qual_cat = px.bar(
            category_df.sort_values('avg_quality_score', ascending=False),
            x='rating_category',
            y='avg_quality_score',
            title="Avg Quality Score by Rating Category",
            labels={'avg_quality_score': 'Quality Score', 'rating_category': 'Category'},
            color='avg_quality_score',
            color_continuous_scale='Greens',
            text='avg_quality_score'
        )
        fig_qual_cat.update_traces(texttemplate='%{text:.1%}', textposition='outside')
        fig_qual_cat.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_qual_cat, use_container_width=True)
    
    st.markdown("---")
    
    # Content Type Split by Rating
    st.subheader("🎬 Content Type Distribution by Rating")
    
    # Top 10 ratings with type split
    top_10_ratings = filtered_df.groupby('rating')['content_count'].sum().nlargest(10).index
    type_split_df = filtered_df[filtered_df['rating'].isin(top_10_ratings)]
    
    fig_type = px.bar(
        type_split_df.sort_values('content_count', ascending=False).head(20),
        x='rating',
        y='content_count',
        color='content_type',
        title="Top 10 Ratings - Movie vs TV Show Split",
        labels={'content_count': 'Content Count', 'rating': 'Rating'},
        color_discrete_sequence=COLOR_PALETTE,
        barmode='group'
    )
    fig_type.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_type, use_container_width=True)
    
    st.markdown("---")
    
    # Duration Analysis by Rating
    st.subheader("🕐 Content Duration by Rating")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average duration by top ratings
        duration_df = filtered_df[filtered_df['avg_duration_value'].notna()].groupby('rating').agg({
            'avg_duration_value': 'mean',
            'content_count': 'sum'
        }).nlargest(10, 'content_count').reset_index()
        
        fig_dur = px.bar(
            duration_df.sort_values('avg_duration_value', ascending=False),
            x='rating',
            y='avg_duration_value',
            title="Avg Duration by Rating (Top 10)",
            labels={'avg_duration_value': 'Avg Duration (min/seasons)', 'rating': 'Rating'},
            color='avg_duration_value',
            color_continuous_scale='Blues',
            text='avg_duration_value'
        )
        fig_dur.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_dur.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_dur, use_container_width=True)
    
    with col2:
        # Content age by rating
        age_df = filtered_df[filtered_df['avg_content_age_years'].notna()].groupby('rating').agg({
            'avg_content_age_years': 'mean',
            'content_count': 'sum'
        }).nlargest(10, 'content_count').reset_index()
        
        fig_age = px.bar(
            age_df.sort_values('avg_content_age_years', ascending=False),
            x='rating',
            y='avg_content_age_years',
            title="Avg Content Age by Rating (Top 10)",
            labels={'avg_content_age_years': 'Avg Age (Years)', 'rating': 'Rating'},
            color='avg_content_age_years',
            color_continuous_scale='YlOrRd',
            text='avg_content_age_years'
        )
        fig_age.update_traces(texttemplate='%{text:.1f}y', textposition='outside')
        fig_age.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_age, use_container_width=True)
    
    st.markdown("---")
    
    # Recent Content by Rating
    st.subheader("📅 Recent Content Additions by Rating")
    
    recent_df = filtered_df.groupby('rating').agg({
        'recent_content_count': 'sum',
        'content_count': 'sum'
    }).reset_index()
    recent_df['recent_percentage'] = (recent_df['recent_content_count'] / recent_df['content_count'] * 100)
    recent_df = recent_df.nlargest(15, 'content_count')
    
    fig_recent = px.bar(
        recent_df.sort_values('recent_content_count', ascending=False),
        x='rating',
        y='recent_content_count',
        title="Recent Content Count by Rating (2021)",
        labels={'recent_content_count': 'Recent Content (2021)', 'rating': 'Rating'},
        color='recent_percentage',
        color_continuous_scale='Purples',
        text='recent_content_count'
    )
    fig_recent.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_recent.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_recent, use_container_width=True)
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Rating Data Table")
    
    display_df = filtered_df.groupby(['rating', 'rating_category', 'content_type']).agg({
        'content_count': 'sum',
        'percentage_of_type': 'mean',
        'avg_quality_score': 'mean',
        'recent_content_count': 'sum',
        'avg_content_age_years': 'mean',
        'avg_duration_value': 'mean'
    }).reset_index()
    
    display_df = display_df.sort_values('content_count', ascending=False).reset_index(drop=True)
    display_df.columns = ['Rating', 'Category', 'Type', 'Count', 'Type %', 'Quality', 'Recent', 'Age (Y)', 'Duration']
    
    st.dataframe(
        display_df.style.format({
            'Count': '{:,.0f}',
            'Type %': '{:.1f}%',
            'Quality': '{:.1%}',
            'Recent': '{:,.0f}',
            'Age (Y)': '{:.1f}',
            'Duration': '{:.1f}'
        }),
        use_container_width=True,
        height=600
    )

else:
    st.error("❌ Failed to load rating data. Please check AWS connection.")

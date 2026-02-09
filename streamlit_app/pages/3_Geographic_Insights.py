"""
Netflix Analytics Dashboard - Geographic Insights Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DataLoader
from config import *

st.set_page_config(
    page_title=f"{PAGE_TITLE} - Geographic Insights",
    page_icon="🌍",
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
st.markdown('<div class="main-header">🌍 Geographic Insights</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explore content distribution across countries and regions.</div>', unsafe_allow_html=True)
st.markdown("---")

# Load data
loader = DataLoader()

with st.spinner("Loading geographic data..."):
    geo_df = loader.load_geographic_distribution()

if not geo_df.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    content_type_filter = st.sidebar.multiselect(
        "Content Type",
        options=geo_df['content_type'].unique(),
        default=geo_df['content_type'].unique()
    )
    
    min_content = st.sidebar.slider(
        "Minimum Content Count",
        min_value=0,
        max_value=int(geo_df['content_count'].max()),
        value=10
    )
    
    # Filter data
    filtered_df = geo_df[
        (geo_df['content_type'].isin(content_type_filter)) &
        (geo_df['content_count'] >= min_content)
    ]
    
    # Key metrics
    st.subheader("🌎 Global Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Countries",
            value=f"{geo_df['primary_country'].nunique()}",
            delta="Global presence"
        )
    
    with col2:
        top_country = geo_df.groupby('primary_country')['content_count'].sum().idxmax()
        top_count = geo_df.groupby('primary_country')['content_count'].sum().max()
        st.metric(
            label="Top Country",
            value=top_country,
            delta=f"{top_count:,} titles"
        )
    
    with col3:
        avg_quality = filtered_df['avg_quality_score'].mean()
        st.metric(
            label="Avg Quality Score",
            value=f"{avg_quality:.1%}",
            delta="Global average"
        )
    
    with col4:
        recent_total = filtered_df['added_2021'].sum()
        st.metric(
            label="Added in 2021",
            value=f"{recent_total:,}",
            delta="Recent additions"
        )
    
    st.markdown("---")
    
    # Top 15 Countries by Content Count
    st.subheader("🏆 Top 15 Countries by Content Count")
    
    top_countries = filtered_df.groupby('primary_country').agg({
        'content_count': 'sum',
        'avg_quality_score': 'mean'
    }).nlargest(15, 'content_count').reset_index()
    
    fig_top = px.bar(
        top_countries,
        x='content_count',
        y='primary_country',
        orientation='h',
        title="Top 15 Countries by Total Content",
        labels={'content_count': 'Content Count', 'primary_country': 'Country'},
        color='avg_quality_score',
        color_continuous_scale='Reds',
        text='content_count'
    )
    fig_top.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
    st.plotly_chart(fig_top, use_container_width=True)
    
    st.markdown("---")
    
    # Movie vs TV Show Distribution by Country
    st.subheader("🎬 Content Type Distribution by Country")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 countries - Movie vs TV Show
        top_10_countries = filtered_df.groupby('primary_country')['content_count'].sum().nlargest(10).index
        top_10_df = filtered_df[filtered_df['primary_country'].isin(top_10_countries)]
        
        fig_type = px.bar(
            top_10_df.sort_values('content_count', ascending=False).head(20),
            x='primary_country',
            y='content_count',
            color='content_type',
            title="Top 10 Countries - Content Type Split",
            labels={'content_count': 'Content Count', 'primary_country': 'Country'},
            color_discrete_sequence=COLOR_PALETTE,
            barmode='group'
        )
        fig_type.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        # Movie percentage by top countries
        country_summary = filtered_df.groupby('primary_country').agg({
            'movie_count': 'sum',
            'tv_show_count': 'sum',
            'content_count': 'sum'
        }).reset_index()
        country_summary['movie_pct'] = (country_summary['movie_count'] / country_summary['content_count'] * 100)
        top_movie_countries = country_summary.nlargest(10, 'content_count')
        
        fig_pct = px.bar(
            top_movie_countries.sort_values('movie_pct', ascending=False),
            x='primary_country',
            y='movie_pct',
            title="Movie Percentage by Country (Top 10)",
            labels={'movie_pct': 'Movie %', 'primary_country': 'Country'},
            color='movie_pct',
            color_continuous_scale='Blues',
            text='movie_pct'
        )
        fig_pct.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_pct.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_pct, use_container_width=True)
    
    st.markdown("---")
    
    # Quality Score Analysis
    st.subheader("⭐ Quality Score by Country")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top quality countries (minimum 20 content pieces)
        quality_countries = filtered_df[filtered_df['content_count'] >= 20].groupby('primary_country').agg({
            'avg_quality_score': 'mean',
            'content_count': 'sum'
        }).nlargest(15, 'avg_quality_score').reset_index()
        
        fig_quality = px.bar(
            quality_countries,
            x='avg_quality_score',
            y='primary_country',
            orientation='h',
            title="Top 15 Countries by Quality Score (Min 20 content)",
            labels={'avg_quality_score': 'Quality Score', 'primary_country': 'Country'},
            color='avg_quality_score',
            color_continuous_scale='Greens',
            text='avg_quality_score'
        )
        fig_quality.update_traces(texttemplate='%{text:.2%}', textposition='outside')
        fig_quality.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Scatter: Content count vs Quality score
        scatter_df = filtered_df.groupby('primary_country').agg({
            'content_count': 'sum',
            'avg_quality_score': 'mean'
        }).reset_index()
        
        fig_scatter = px.scatter(
            scatter_df,
            x='content_count',
            y='avg_quality_score',
            size='content_count',
            hover_name='primary_country',
            title="Content Volume vs Quality Score",
            labels={'content_count': 'Total Content Count', 'avg_quality_score': 'Avg Quality Score'},
            color='avg_quality_score',
            color_continuous_scale='RdYlGn'
        )
        fig_scatter.update_layout(height=600)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # Recent Content Additions (2019-2021)
    st.subheader("📅 Recent Content Additions by Country")
    
    # Aggregate recent additions
    recent_df = filtered_df.groupby('primary_country').agg({
        'added_2019': 'sum',
        'added_2020': 'sum',
        'added_2021': 'sum',
        'content_count': 'sum'
    }).nlargest(10, 'content_count').reset_index()
    
    # Reshape for grouped bar chart
    recent_melted = recent_df.melt(
        id_vars='primary_country',
        value_vars=['added_2019', 'added_2020', 'added_2021'],
        var_name='Year',
        value_name='Content Added'
    )
    recent_melted['Year'] = recent_melted['Year'].str.replace('added_', '')
    
    fig_recent = px.bar(
        recent_melted,
        x='primary_country',
        y='Content Added',
        color='Year',
        title="Content Additions by Year (Top 10 Countries)",
        labels={'Content Added': 'Content Count', 'primary_country': 'Country'},
        color_discrete_sequence=COLOR_PALETTE,
        barmode='group'
    )
    fig_recent.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_recent, use_container_width=True)
    
    st.markdown("---")
    
    # Content Age Analysis
    st.subheader("🕰️ Content Age by Country")
    
    age_df = filtered_df.groupby('primary_country').agg({
        'avg_content_age_years': 'mean',
        'content_count': 'sum'
    }).nlargest(15, 'content_count').reset_index()
    
    fig_age = px.bar(
        age_df.sort_values('avg_content_age_years', ascending=False),
        x='primary_country',
        y='avg_content_age_years',
        title="Average Content Age by Country (Top 15)",
        labels={'avg_content_age_years': 'Avg Age (Years)', 'primary_country': 'Country'},
        color='avg_content_age_years',
        color_continuous_scale='YlOrRd',
        text='avg_content_age_years'
    )
    fig_age.update_traces(texttemplate='%{text:.1f}y', textposition='outside')
    fig_age.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_age, use_container_width=True)
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Country Data Table")
    
    display_df = filtered_df.groupby('primary_country').agg({
        'content_count': 'sum',
        'movie_count': 'sum',
        'tv_show_count': 'sum',
        'avg_quality_score': 'mean',
        'added_2021': 'sum',
        'avg_content_age_years': 'mean'
    }).reset_index()
    
    display_df = display_df.sort_values('content_count', ascending=False).reset_index(drop=True)
    display_df.columns = ['Country', 'Total Content', 'Movies', 'TV Shows', 'Avg Quality', 'Added 2021', 'Avg Age (Years)']
    
    st.dataframe(
        display_df.style.format({
            'Total Content': '{:,.0f}',
            'Movies': '{:,.0f}',
            'TV Shows': '{:,.0f}',
            'Avg Quality': '{:.1%}',
            'Added 2021': '{:,.0f}',
            'Avg Age (Years)': '{:.1f}'
        }),
        use_container_width=True,
        height=600
    )

else:
    st.error("❌ Failed to load geographic data. Please check AWS connection.")

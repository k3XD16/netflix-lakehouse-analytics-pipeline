"""
Netflix Analytics Dashboard - Top Producers Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DataLoader
from config import *
import ast

st.set_page_config(
    page_title=f"{PAGE_TITLE} - Top Producers",
    page_icon="🎬",
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
st.markdown('<div class="main-header">🎬 Top Producers</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explore top directors and their contributions to Netflix catalog.</div>', unsafe_allow_html=True)
st.markdown("---")

# Load data
loader = DataLoader()

with st.spinner("Loading producer data..."):
    producer_df = loader.load_top_producers()

if not producer_df.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    content_type_filter = st.sidebar.multiselect(
        "Content Type",
        options=producer_df['content_type'].unique(),
        default=producer_df['content_type'].unique()
    )
    
    min_content = st.sidebar.slider(
        "Minimum Content Count",
        min_value=1,
        max_value=int(producer_df['content_count'].max()),
        value=3
    )
    
    # Filter data
    filtered_df = producer_df[
        (producer_df['content_type'].isin(content_type_filter)) &
        (producer_df['content_count'] >= min_content)
    ]
    
    # Key metrics
    st.subheader("📊 Producer Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Producers",
            value=f"{filtered_df['director'].nunique():,}",
            delta="In dataset"
        )
    
    with col2:
        top_producer = filtered_df.loc[filtered_df['content_count'].idxmax()]
        st.metric(
            label="Most Prolific",
            value=top_producer['director'],
            delta=f"{top_producer['content_count']:.0f} titles"
        )
    
    with col3:
        avg_quality = filtered_df['avg_quality_score'].mean()
        st.metric(
            label="Avg Quality Score",
            value=f"{avg_quality:.1%}",
            delta="Producer average"
        )
    
    with col4:
        avg_years_active = filtered_df['years_active'].mean()
        st.metric(
            label="Avg Years Active",
            value=f"{avg_years_active:.1f}",
            delta="Career span"
        )
    
    st.markdown("---")
    
    # Top 20 Producers by Content Count
    st.subheader("🏆 Top 20 Most Prolific Producers")
    
    top_20 = filtered_df.nlargest(20, 'content_count')
    
    fig_top = px.bar(
        top_20,
        x='content_count',
        y='director',
        orientation='h',
        title="Top 20 Producers by Content Count",
        labels={'content_count': 'Content Count', 'director': 'Director/Producer'},
        color='content_type',
        color_discrete_sequence=COLOR_PALETTE,
        text='content_count'
    )
    fig_top.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=700)
    st.plotly_chart(fig_top, use_container_width=True)
    
    st.markdown("---")
    
    # Quality Score Analysis
    st.subheader("⭐ Producer Quality Scores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top producers by quality (min 5 content)
        quality_producers = filtered_df[filtered_df['content_count'] >= 5].nlargest(15, 'avg_quality_score')
        
        fig_quality = px.bar(
            quality_producers,
            x='avg_quality_score',
            y='director',
            orientation='h',
            title="Top 15 Producers by Quality Score (Min 5 content)",
            labels={'avg_quality_score': 'Quality Score', 'director': 'Director'},
            color='avg_quality_score',
            color_continuous_scale='Greens',
            text='avg_quality_score'
        )
        fig_quality.update_traces(texttemplate='%{text:.2%}', textposition='outside')
        fig_quality.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Scatter: Content count vs Quality
        scatter_df = filtered_df[filtered_df['content_count'] >= 3]
        
        fig_scatter = px.scatter(
            scatter_df,
            x='content_count',
            y='avg_quality_score',
            size='content_count',
            hover_name='director',
            title="Productivity vs Quality (Min 3 content)",
            labels={'content_count': 'Content Count', 'avg_quality_score': 'Quality Score'},
            color='content_type',
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_scatter.update_layout(height=600)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # Career Span Analysis
    st.subheader("📅 Career Span Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Years active distribution
        career_df = filtered_df[filtered_df['years_active'] > 0].nlargest(20, 'content_count')
        
        fig_career = px.bar(
            career_df,
            x='director',
            y='years_active',
            title="Career Span (Top 20 Producers)",
            labels={'years_active': 'Years Active on Netflix', 'director': 'Director'},
            color='years_active',
            color_continuous_scale='Blues',
            text='years_active'
        )
        fig_career.update_traces(texttemplate='%{text:.0f}y', textposition='outside')
        fig_career.update_layout(xaxis_tickangle=-45, height=600)
        st.plotly_chart(fig_career, use_container_width=True)
    
    with col2:
        # Release year timeline
        timeline_df = filtered_df[filtered_df['content_count'] >= 5].nlargest(15, 'content_count')
        
        fig_timeline = go.Figure()
        
        for idx, row in timeline_df.iterrows():
            fig_timeline.add_trace(go.Scatter(
                x=[row['first_release_year'], row['latest_release_year']],
                y=[row['director'], row['director']],
                mode='lines+markers',
                name=row['director'],
                line=dict(width=4),
                showlegend=False,
                hovertemplate=f"{row['director']}<br>%{{x}}<extra></extra>"
            ))
        
        fig_timeline.update_layout(
            title="Career Timeline (Top 15 Producers)",
            xaxis_title="Year",
            yaxis_title="Director",
            height=600,
            hovermode='closest'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # Genre Specialization
    st.subheader("🎭 Genre Specialization")
    
    # Parse genres_worked_in (assuming it's a string representation of list)
    def count_genres(genres_str):
        try:
            genres_list = ast.literal_eval(genres_str) if isinstance(genres_str, str) else genres_str
            return len(genres_list) if isinstance(genres_list, list) else 0
        except:
            return 0
    
    filtered_df['genre_count'] = filtered_df['genres_worked_in'].apply(count_genres)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Genre diversity
        diversity_df = filtered_df[filtered_df['content_count'] >= 5].nlargest(15, 'genre_count')
        
        fig_diversity = px.bar(
            diversity_df,
            x='director',
            y='genre_count',
            title="Most Diverse Producers (Min 5 content)",
            labels={'genre_count': 'Number of Genres', 'director': 'Director'},
            color='genre_count',
            color_continuous_scale='Purples',
            text='genre_count'
        )
        fig_diversity.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_diversity.update_layout(xaxis_tickangle=-45, height=600)
        st.plotly_chart(fig_diversity, use_container_width=True)
    
    with col2:
        # Specialists vs Generalists
        filtered_df['producer_type'] = filtered_df['genre_count'].apply(
            lambda x: 'Specialist (1-2)' if x <= 2 else ('Moderate (3-4)' if x <= 4 else 'Generalist (5+)')
        )
        
        type_dist = filtered_df.groupby('producer_type')['content_count'].sum().reset_index()
        
        fig_type = px.pie(
            type_dist,
            values='content_count',
            names='producer_type',
            title="Producer Type Distribution",
            color_discrete_sequence=COLOR_PALETTE,
            hole=0.4
        )
        fig_type.update_traces(textposition='inside', textinfo='percent+label')
        fig_type.update_layout(height=600)
        st.plotly_chart(fig_type, use_container_width=True)
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("🆕 Recent Producer Activity")
    
    # Producers with recent works
    recent_producers = filtered_df[filtered_df['recent_works_count'] > 0].nlargest(20, 'recent_works_count')
    
    if not recent_producers.empty:
        fig_recent = px.bar(
            recent_producers,
            x='director',
            y='recent_works_count',
            title="Producers with Recent Works (2021)",
            labels={'recent_works_count': 'Recent Works Count', 'director': 'Director'},
            color='content_type',
            color_discrete_sequence=COLOR_PALETTE,
            text='recent_works_count'
        )
        fig_recent.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_recent.update_layout(xaxis_tickangle=-45, height=600)
        st.plotly_chart(fig_recent, use_container_width=True)
    else:
        st.info("No producers with recent works (2021) in filtered dataset.")
    
    st.markdown("---")
    
    # Producer Search
    st.subheader("🔍 Producer Search")
    
    search_query = st.text_input("Search for a producer:", placeholder="Enter director name...")
    
    if search_query:
        search_results = filtered_df[filtered_df['director'].str.contains(search_query, case=False, na=False)]
        
        if not search_results.empty:
            st.success(f"Found {len(search_results)} producer(s) matching '{search_query}'")
            
            for idx, row in search_results.head(10).iterrows():
                with st.expander(f"🎬 {row['director']} ({row['content_type']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Content Count", f"{row['content_count']:.0f}")
                        st.metric("Quality Score", f"{row['avg_quality_score']:.1%}")
                    
                    with col2:
                        st.metric("First Release", f"{row['first_release_year']:.0f}")
                        st.metric("Latest Release", f"{row['latest_release_year']:.0f}")
                    
                    with col3:
                        st.metric("Years Active", f"{row['years_active']:.0f}")
                        st.metric("Recent Works", f"{row['recent_works_count']:.0f}")
                    
                    st.write(f"**Genres:** {row['genres_worked_in']}")
        else:
            st.warning(f"No producers found matching '{search_query}'")
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Producer Data Table")
    
    display_df = filtered_df[['director', 'content_type', 'content_count', 'avg_quality_score',
                              'first_release_year', 'latest_release_year', 'years_active', 
                              'recent_works_count', 'rank_by_volume']].copy()
    
    display_df = display_df.sort_values('content_count', ascending=False).reset_index(drop=True)
    display_df.columns = ['Director', 'Type', 'Content', 'Quality', 'First Year', 
                          'Latest Year', 'Years Active', 'Recent', 'Rank']
    
    st.dataframe(
        display_df.head(100).style.format({
            'Content': '{:.0f}',
            'Quality': '{:.1%}',
            'First Year': '{:.0f}',
            'Latest Year': '{:.0f}',
            'Years Active': '{:.0f}',
            'Recent': '{:.0f}',
            'Rank': '{:.0f}'
        }),
        use_container_width=True,
        height=600
    )
    
    # Download option
    st.download_button(
        label="📥 Download Producer Data (CSV)",
        data=display_df.to_csv(index=False).encode('utf-8'),
        file_name='netflix_top_producers.csv',
        mime='text/csv'
    )

else:
    st.error("❌ Failed to load producer data. Please check AWS connection.")

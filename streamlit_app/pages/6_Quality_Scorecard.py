"""
Netflix Analytics Dashboard - Quality Scorecard Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DataLoader
from config import *

st.set_page_config(
    page_title=f"{PAGE_TITLE} - Quality Scorecard",
    page_icon="✅",
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
st.markdown('<div class="main-header">✅ Quality Scorecard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Data quality metrics and completeness analysis.</div>', unsafe_allow_html=True)
st.markdown("---")

# Load data
loader = DataLoader()

with st.spinner("Loading quality data..."):
    quality_df = loader.load_quality_scorecard()

if not quality_df.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    content_type_filter = st.sidebar.multiselect(
        "Content Type",
        options=quality_df['content_type'].unique(),
        default=quality_df['content_type'].unique()
    )
    
    # Filter data
    filtered_df = quality_df[quality_df['content_type'].isin(content_type_filter)]
    
    # Key metrics
    st.subheader("📊 Quality Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        excellent_count = filtered_df[filtered_df['quality_tier'] == 'Excellent (0.9-1.0)']['content_count'].sum()
        total_count = filtered_df['content_count'].sum()
        excellent_pct = (excellent_count / total_count * 100) if total_count > 0 else 0
        st.metric(
            label="Excellent Quality",
            value=f"{excellent_pct:.1f}%",
            delta=f"{excellent_count:,.0f} titles"
        )
    
    with col2:
        good_count = filtered_df[filtered_df['quality_tier'] == 'Good (0.7-0.89)']['content_count'].sum()
        good_pct = (good_count / total_count * 100) if total_count > 0 else 0
        st.metric(
            label="Good Quality",
            value=f"{good_pct:.1f}%",
            delta=f"{good_count:,.0f} titles"
        )
    
    with col3:
        avg_quality = filtered_df['avg_quality_score'].mean()
        st.metric(
            label="Avg Quality Score",
            value=f"{avg_quality:.1%}",
            delta="Overall average"
        )
    
    with col4:
        avg_director_completeness = filtered_df['has_director_pct'].mean()
        st.metric(
            label="Director Completeness",
            value=f"{avg_director_completeness:.1f}%",
            delta="Field completeness"
        )
    
    st.markdown("---")
    
    # Quality Tier Distribution
    st.subheader("📊 Quality Tier Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        tier_summary = filtered_df.groupby('quality_tier')['content_count'].sum().reset_index()
        
        fig_pie = px.pie(
            tier_summary,
            values='content_count',
            names='quality_tier',
            title="Content Distribution by Quality Tier",
            color_discrete_sequence=COLOR_PALETTE,
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart by content type
        type_quality = filtered_df.groupby(['content_type', 'quality_tier']).agg({
            'content_count': 'sum'
        }).reset_index()
        
        fig_bar = px.bar(
            type_quality,
            x='quality_tier',
            y='content_count',
            color='content_type',
            title="Quality Tier by Content Type",
            labels={'content_count': 'Content Count', 'quality_tier': 'Quality Tier'},
            color_discrete_sequence=COLOR_PALETTE,
            barmode='group'
        )
        fig_bar.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Quality Score Analysis
    st.subheader("⭐ Quality Score Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average quality score by tier
        quality_avg = filtered_df.groupby('quality_tier').agg({
            'avg_quality_score': 'mean',
            'content_count': 'sum'
        }).reset_index()
        
        # Define order
        tier_order = ['Excellent (0.9-1.0)', 'Good (0.7-0.89)', 'Fair (0.5-0.69)', 'Poor (<0.5)']
        quality_avg['quality_tier'] = pd.Categorical(quality_avg['quality_tier'], categories=tier_order, ordered=True)
        quality_avg = quality_avg.sort_values('quality_tier')
        
        fig_qual = px.bar(
            quality_avg,
            x='quality_tier',
            y='avg_quality_score',
            title="Average Quality Score by Tier",
            labels={'avg_quality_score': 'Avg Quality Score', 'quality_tier': 'Quality Tier'},
            color='avg_quality_score',
            color_continuous_scale='Greens',
            text='avg_quality_score'
        )
        fig_qual.update_traces(texttemplate='%{text:.1%}', textposition='outside')
        fig_qual.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_qual, use_container_width=True)
    
    with col2:
        # Content count by tier
        fig_count = px.bar(
            quality_avg,
            x='quality_tier',
            y='content_count',
            title="Content Count by Quality Tier",
            labels={'content_count': 'Content Count', 'quality_tier': 'Quality Tier'},
            color='content_count',
            color_continuous_scale='Reds',
            text='content_count'
        )
        fig_count.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_count.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_count, use_container_width=True)
    
    st.markdown("---")
    
    # Field Completeness Analysis
    st.subheader("📝 Field Completeness by Quality Tier")
    
    # Director completeness
    col1, col2 = st.columns(2)
    
    with col1:
        fig_director = px.bar(
            quality_avg,
            x='quality_tier',
            y=filtered_df.groupby('quality_tier')['has_director_pct'].mean().values,
            title="Director Field Completeness by Tier",
            labels={'y': 'Director Completeness %', 'quality_tier': 'Quality Tier'},
            color=filtered_df.groupby('quality_tier')['has_director_pct'].mean().values,
            color_continuous_scale='Blues',
            text=filtered_df.groupby('quality_tier')['has_director_pct'].mean().values
        )
        fig_director.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_director.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_director, use_container_width=True)
    
    with col2:
        # Cast completeness
        fig_cast = px.bar(
            quality_avg,
            x='quality_tier',
            y=filtered_df.groupby('quality_tier')['has_cast_pct'].mean().values,
            title="Cast Field Completeness by Tier",
            labels={'y': 'Cast Completeness %', 'quality_tier': 'Quality Tier'},
            color=filtered_df.groupby('quality_tier')['has_cast_pct'].mean().values,
            color_continuous_scale='Purples',
            text=filtered_df.groupby('quality_tier')['has_cast_pct'].mean().values
        )
        fig_cast.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_cast.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_cast, use_container_width=True)
    
    st.markdown("---")
    
    # Field Availability Heatmap
    st.subheader("🔥 Field Availability Heatmap")
    
    # Prepare heatmap data
    heatmap_data = filtered_df.groupby('quality_tier').agg({
        'has_director_pct': 'mean',
        'has_cast_pct': 'mean',
        'has_duration_count': 'sum',
        'has_date_added_count': 'sum',
        'has_release_year_count': 'sum'
    }).reset_index()
    
    # Calculate percentages for count fields
    heatmap_data['duration_pct'] = (heatmap_data['has_duration_count'] / filtered_df.groupby('quality_tier')['content_count'].sum().values * 100)
    heatmap_data['date_added_pct'] = (heatmap_data['has_date_added_count'] / filtered_df.groupby('quality_tier')['content_count'].sum().values * 100)
    heatmap_data['release_year_pct'] = (heatmap_data['has_release_year_count'] / filtered_df.groupby('quality_tier')['content_count'].sum().values * 100)
    
    heatmap_matrix = heatmap_data[['has_director_pct', 'has_cast_pct', 'duration_pct', 'date_added_pct', 'release_year_pct']].T
    heatmap_matrix.columns = heatmap_data['quality_tier']
    heatmap_matrix.index = ['Director', 'Cast', 'Duration', 'Date Added', 'Release Year']
    
    fig_heatmap = px.imshow(
        heatmap_matrix,
        labels=dict(x="Quality Tier", y="Field", color="Completeness %"),
        title="Field Completeness Heatmap",
        color_continuous_scale='RdYlGn',
        aspect='auto',
        text_auto='.1f'
    )
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Quality by Content Type
    st.subheader("🎬 Quality Distribution by Content Type")
    
    type_quality_detail = filtered_df.groupby(['content_type', 'quality_tier']).agg({
        'content_count': 'sum',
        'percentage_of_type': 'mean',
        'avg_quality_score': 'mean'
    }).reset_index()
    
    fig_type_quality = px.sunburst(
        type_quality_detail,
        path=['content_type', 'quality_tier'],
        values='content_count',
        title="Quality Distribution Hierarchy",
        color='avg_quality_score',
        color_continuous_scale='RdYlGn'
    )
    fig_type_quality.update_layout(height=600)
    st.plotly_chart(fig_type_quality, use_container_width=True)
    
    st.markdown("---")
    
    # Quality Improvements Recommendations
    st.subheader("💡 Data Quality Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **High Quality Content (≥0.9)**
        - Majority of catalog maintains excellent data quality
        - Complete metadata across all critical fields
        - Suitable for production analytics and reporting
        """)
        
        st.success("""
        **Strengths:**
        - ✅ High cast completeness (90%+)
        - ✅ Consistent duration data
        - ✅ Complete date and year information
        """)
    
    with col2:
        # Calculate improvement areas
        poor_quality = filtered_df[filtered_df['quality_tier'].str.contains('Poor|Fair')]
        if not poor_quality.empty:
            st.warning("""
            **Areas for Improvement:**
            - ⚠️ Director information gaps in some content
            - ⚠️ Legacy content may have incomplete metadata
            - ⚠️ Documentary content shows lower completeness
            """)
        
        st.info(f"""
        **Overall Assessment:**
        - Overall Quality Score: {avg_quality:.1%}
        - High Quality Content: {excellent_pct:.1f}%
        - Data Pipeline Health: Excellent ✅
        """)
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Quality Scorecard Table")
    
    display_df = filtered_df[['content_type', 'quality_tier', 'content_count', 'percentage_of_type',
                              'avg_quality_score', 'has_director_pct', 'has_cast_pct']].copy()
    
    display_df = display_df.sort_values(['content_type', 'content_count'], ascending=[True, False]).reset_index(drop=True)
    display_df.columns = ['Type', 'Quality Tier', 'Count', 'Type %', 'Avg Score', 'Director %', 'Cast %']
    
    st.dataframe(
        display_df.style.format({
            'Count': '{:,.0f}',
            'Type %': '{:.1f}%',
            'Avg Score': '{:.1%}',
            'Director %': '{:.1f}%',
            'Cast %': '{:.1f}%'
        }),
        use_container_width=True,
        height=500
    )
    
    # Download option
    st.download_button(
        label="📥 Download Quality Scorecard (CSV)",
        data=display_df.to_csv(index=False).encode('utf-8'),
        file_name='netflix_quality_scorecard.csv',
        mime='text/csv'
    )

else:
    st.error("❌ Failed to load quality data. Please check AWS connection.")

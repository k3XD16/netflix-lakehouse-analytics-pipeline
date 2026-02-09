"""
Netflix Analytics Dashboard - Temporal Trends Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DataLoader
from config import *

st.set_page_config(
    page_title=f"{PAGE_TITLE} - Temporal Trends",
    page_icon="📈",
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
st.markdown('<div class="main-header">📈 Temporal Trends</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analyze content addition patterns over time.</div>', unsafe_allow_html=True)
st.markdown("---")

# Load data
loader = DataLoader()

with st.spinner("Loading temporal data..."):
    temporal_df = loader.load_temporal_trends()

if not temporal_df.empty:
    # Convert columns to appropriate types
    temporal_df['added_year'] = temporal_df['added_year'].astype(int)
    temporal_df['added_month'] = temporal_df['added_month'].astype(int)
    temporal_df['year_month'] = pd.to_datetime(
        temporal_df['added_year'].astype(str) + '-' + temporal_df['added_month'].astype(str),
        format='%Y-%m'
    )
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=int(temporal_df['added_year'].min()),
        max_value=int(temporal_df['added_year'].max()),
        value=(int(temporal_df['added_year'].min()), int(temporal_df['added_year'].max()))
    )
    
    content_type_filter = st.sidebar.multiselect(
        "Content Type",
        options=temporal_df['content_type'].unique(),
        default=temporal_df['content_type'].unique()
    )
    
    # Filter data
    filtered_df = temporal_df[
        (temporal_df['added_year'] >= year_range[0]) &
        (temporal_df['added_year'] <= year_range[1]) &
        (temporal_df['content_type'].isin(content_type_filter))
    ]
    
    # Key metrics
    st.subheader("📊 Temporal Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_added = filtered_df['content_added_count'].sum()
        st.metric(
            label="Total Content Added",
            value=f"{total_added:,}",
            delta="In selected period"
        )
    
    with col2:
        peak_month = filtered_df.loc[filtered_df['content_added_count'].idxmax()]
        st.metric(
            label="Peak Month",
            value=f"{peak_month['month_name']} {peak_month['added_year']:.0f}",
            delta=f"{peak_month['content_added_count']:.0f} titles"
        )
    
    with col3:
        avg_monthly = filtered_df.groupby('year_month')['content_added_count'].sum().mean()
        st.metric(
            label="Avg Monthly Additions",
            value=f"{avg_monthly:.0f}",
            delta="Per month"
        )
    
    with col4:
        avg_quality = filtered_df['avg_quality_score'].mean()
        st.metric(
            label="Avg Quality Score",
            value=f"{avg_quality:.1%}",
            delta="Across timeline"
        )
    
    st.markdown("---")
    
    # Monthly Content Additions Over Time
    st.subheader("📅 Monthly Content Additions Timeline")
    
    # Aggregate by year_month and content_type
    monthly_agg = filtered_df.groupby(['year_month', 'content_type']).agg({
        'content_added_count': 'sum'
    }).reset_index()
    
    fig_timeline = px.line(
        monthly_agg,
        x='year_month',
        y='content_added_count',
        color='content_type',
        title="Content Additions Over Time (Monthly)",
        labels={'content_added_count': 'Content Added', 'year_month': 'Date'},
        color_discrete_sequence=COLOR_PALETTE,
        markers=True
    )
    fig_timeline.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # Cumulative Growth
    st.subheader("📊 Cumulative Content Growth")
    
    # Calculate cumulative sum by content type
    cumulative_df = filtered_df.sort_values('year_month').groupby(['year_month', 'content_type']).agg({
        'content_added_count': 'sum'
    }).reset_index()
    cumulative_df['cumulative_count'] = cumulative_df.groupby('content_type')['content_added_count'].cumsum()
    
    fig_cumulative = px.line(
        cumulative_df,
        x='year_month',
        y='cumulative_count',
        color='content_type',
        title="Cumulative Content Growth",
        labels={'cumulative_count': 'Cumulative Count', 'year_month': 'Date'},
        color_discrete_sequence=COLOR_PALETTE,
        markers=True
    )
    fig_cumulative.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig_cumulative, use_container_width=True)
    
    st.markdown("---")
    
    # Yearly Comparison
    st.subheader("📆 Year-over-Year Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Total additions by year
        yearly_df = filtered_df.groupby(['added_year', 'content_type']).agg({
            'content_added_count': 'sum'
        }).reset_index()
        
        fig_yearly = px.bar(
            yearly_df,
            x='added_year',
            y='content_added_count',
            color='content_type',
            title="Annual Content Additions",
            labels={'content_added_count': 'Content Added', 'added_year': 'Year'},
            color_discrete_sequence=COLOR_PALETTE,
            barmode='group'
        )
        fig_yearly.update_layout(height=500)
        st.plotly_chart(fig_yearly, use_container_width=True)
    
    with col2:
        # Average quality by year
        quality_yearly = filtered_df.groupby(['added_year', 'content_type']).agg({
            'avg_quality_score': 'mean'
        }).reset_index()
        
        fig_qual_year = px.line(
            quality_yearly,
            x='added_year',
            y='avg_quality_score',
            color='content_type',
            title="Quality Score Trend by Year",
            labels={'avg_quality_score': 'Avg Quality Score', 'added_year': 'Year'},
            color_discrete_sequence=COLOR_PALETTE,
            markers=True
        )
        fig_qual_year.update_layout(height=500)
        st.plotly_chart(fig_qual_year, use_container_width=True)
    
    st.markdown("---")
    
    # Monthly Seasonality Analysis
    st.subheader("🌡️ Monthly Seasonality Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average content by month (across all years)
        monthly_pattern = filtered_df.groupby(['added_month', 'month_name']).agg({
            'content_added_count': 'mean'
        }).reset_index().sort_values('added_month')
        
        fig_season = px.bar(
            monthly_pattern,
            x='month_name',
            y='content_added_count',
            title="Average Content Additions by Month",
            labels={'content_added_count': 'Avg Content Added', 'month_name': 'Month'},
            color='content_added_count',
            color_continuous_scale='Reds',
            text='content_added_count'
        )
        fig_season.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_season.update_layout(height=500)
        st.plotly_chart(fig_season, use_container_width=True)
    
    with col2:
        # Heatmap of content additions
        heatmap_data = filtered_df.pivot_table(
            values='content_added_count',
            index='added_month',
            columns='added_year',
            aggfunc='sum',
            fill_value=0
        )
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Year", y="Month", color="Content Count"),
            title="Content Additions Heatmap",
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Content Age Trends
    st.subheader("🕰️ Content Age at Addition")
    
    age_trend = filtered_df.groupby(['year_month', 'content_type']).agg({
        'avg_age_of_content_added': 'mean'
    }).reset_index()
    
    fig_age = px.line(
        age_trend,
        x='year_month',
        y='avg_age_of_content_added',
        color='content_type',
        title="Average Age of Content When Added",
        labels={'avg_age_of_content_added': 'Avg Age (Years)', 'year_month': 'Date'},
        color_discrete_sequence=COLOR_PALETTE,
        markers=True
    )
    fig_age.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig_age, use_container_width=True)
    
    st.markdown("---")
    
    # Top Performing Months
    st.subheader("🏆 Top Performing Months")
    
    top_months = filtered_df.groupby(['added_year', 'added_month', 'month_name']).agg({
        'content_added_count': 'sum',
        'avg_quality_score': 'mean'
    }).reset_index().nlargest(20, 'content_added_count')
    
    top_months['year_month_label'] = top_months['month_name'] + ' ' + top_months['added_year'].astype(str)
    
    fig_top = px.bar(
        top_months,
        x='year_month_label',
        y='content_added_count',
        title="Top 20 Months by Content Additions",
        labels={'content_added_count': 'Content Added', 'year_month_label': 'Month-Year'},
        color='avg_quality_score',
        color_continuous_scale='Greens',
        text='content_added_count'
    )
    fig_top.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_top.update_layout(xaxis_tickangle=-45, height=600)
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Temporal Data Table")
    
    display_df = filtered_df.groupby(['added_year', 'added_month', 'month_name', 'content_type']).agg({
        'content_added_count': 'sum',
        'cumulative_content_count': 'max',
        'avg_quality_score': 'mean',
        'avg_age_of_content_added': 'mean'
    }).reset_index()
    
    display_df = display_df.sort_values(['added_year', 'added_month'], ascending=[False, False]).reset_index(drop=True)
    display_df.columns = ['Year', 'Month #', 'Month', 'Type', 'Added', 'Cumulative', 'Quality', 'Avg Age']
    
    st.dataframe(
        display_df.head(100).style.format({
            'Added': '{:,.0f}',
            'Cumulative': '{:,.0f}',
            'Quality': '{:.1%}',
            'Avg Age': '{:.1f}'
        }),
        use_container_width=True,
        height=600
    )
    
    # Download data
    st.download_button(
        label="📥 Download Temporal Data (CSV)",
        data=display_df.to_csv(index=False).encode('utf-8'),
        file_name='netflix_temporal_trends.csv',
        mime='text/csv'
    )

else:
    st.error("❌ Failed to load temporal data. Please check AWS connection.")

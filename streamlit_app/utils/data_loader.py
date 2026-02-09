"""
Data Loader - Load curated gold layer data
"""
import pandas as pd
import streamlit as st
from pathlib import Path
from utils.aws_connector import AWSConnector
from config import *

class DataLoader:
    """Load and cache gold layer data"""
    
    def __init__(self):
        self.aws = AWSConnector(AWS_REGION)
    
    @st.cache_data(ttl=3600)
    def load_content_overview(_self) -> pd.DataFrame:
        """Load content overview table"""
        return _self.aws.read_table(GLUE_CURATED_DB, "netflix_gold_content_overview")
    
    @st.cache_data(ttl=3600)
    def load_genre_analysis(_self) -> pd.DataFrame:
        """Load genre analysis table"""
        return _self.aws.read_table(GLUE_CURATED_DB, "netflix_gold_genre_analysis")
    
    @st.cache_data(ttl=3600)
    def load_geographic_distribution(_self) -> pd.DataFrame:
        """Load geographic distribution table"""
        return _self.aws.read_table(GLUE_CURATED_DB, "netflix_gold_geographic_distribution")
    
    @st.cache_data(ttl=3600)
    def load_rating_distribution(_self) -> pd.DataFrame:
        """Load rating distribution table"""
        return _self.aws.read_table(GLUE_CURATED_DB, "netflix_gold_rating_distribution")
    
    @st.cache_data(ttl=3600)
    def load_temporal_trends(_self) -> pd.DataFrame:
        """Load temporal trends table"""
        return _self.aws.read_table(GLUE_CURATED_DB, "netflix_gold_temporal_trends")
    
    @st.cache_data(ttl=3600)
    def load_quality_scorecard(_self) -> pd.DataFrame:
        """Load quality scorecard table"""
        return _self.aws.read_table(GLUE_CURATED_DB, "netflix_gold_quality_scorecard")
    
    @st.cache_data(ttl=3600)
    def load_top_producers(_self) -> pd.DataFrame:
        """Load top producers table"""
        return _self.aws.read_table(GLUE_CURATED_DB, "netflix_gold_top_producers")
    
    def load_all_tables(self) -> dict:
        """Load all gold layer tables into dictionary"""
        return {
            "content_overview": self.load_content_overview(),
            "genre_analysis": self.load_genre_analysis(),
            "geographic": self.load_geographic_distribution(),
            "rating": self.load_rating_distribution(),
            "temporal": self.load_temporal_trends(),
            "quality": self.load_quality_scorecard(),
            "producers": self.load_top_producers()
        }
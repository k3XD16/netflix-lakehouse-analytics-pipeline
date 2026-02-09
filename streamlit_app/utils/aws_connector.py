"""
AWS Data Connector - Athena and S3 utilities
"""
import boto3
import pandas as pd
import awswrangler as wr
from typing import Optional
import streamlit as st

class AWSConnector:
    """Handle AWS Athena and S3 connections"""
    
    def __init__(self, region: str = "ap-south-1"):
        self.region = region
        self.session = boto3.Session(region_name=region)
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def query_athena(_self, query: str, database: str) -> pd.DataFrame:
        """
        Execute Athena query and return results as DataFrame
        
        Args:
            query: SQL query to execute
            database: Athena database name
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            df = wr.athena.read_sql_query(
                sql=query,
                database=database,
                boto3_session=_self.session
            )
            return df
        except Exception as e:
            st.error(f"Athena query failed: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def read_table(_self, database: str, table: str) -> pd.DataFrame:
        """
        Read entire Glue table via Athena
        
        Args:
            database: Glue database name
            table: Glue table name
            
        Returns:
            pd.DataFrame: Table data
        """
        query = f"SELECT * FROM {database}.{table}"
        return _self.query_athena(query, database)
    
    @st.cache_data(ttl=3600)
    def read_s3_csv(_self, s3_path: str) -> pd.DataFrame:
        """
        Read CSV file from S3
        
        Args:
            s3_path: S3 path (s3://bucket/key)
            
        Returns:
            pd.DataFrame: CSV data
        """
        try:
            df = wr.s3.read_csv(
                path=s3_path,
                boto3_session=_self.session
            )
            return df
        except Exception as e:
            st.error(f"S3 read failed: {e}")
            return pd.DataFrame()
    
    def list_s3_objects(self, s3_prefix: str) -> list:
        """
        List objects in S3 prefix
        
        Args:
            s3_prefix: S3 prefix path
            
        Returns:
            list: Object keys
        """
        try:
            objects = wr.s3.list_objects(
                path=s3_prefix,
                boto3_session=self.session
            )
            return objects
        except Exception as e:
            st.error(f"S3 list failed: {e}")
            return []
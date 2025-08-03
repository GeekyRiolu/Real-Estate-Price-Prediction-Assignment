import pandas as pd
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyDataIngestion:
    def __init__(self, baanknet_file: str, property_details_dir: str):
        self.baanknet_file = baanknet_file
        self.property_details_dir = property_details_dir
        self.unified_schema = {
            'id': None,
            'borrower_name': None,
            'bank_name': None,
            'address': None,
            'price': None,
            'dimensions': None,
            'area_sqft': None,
            'emd': None,
            'possession': None,
            'auction_date': None,
            'application_deadline': None,
            'locality': None,
            'city': None,
            'state': None,
            'pincode': None,
            'property_type': None,
            'description': None,
            'source': None
        }
    
    def extract_area_from_dimensions(self, dimensions: str) -> Optional[float]:
        """Extract area in square feet from dimension strings"""
        if not dimensions or pd.isna(dimensions):
            return None
        
        # Convert to lowercase for easier matching
        dim_lower = str(dimensions).lower()
        
        # Patterns for different area formats
        patterns = [
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*ft\.?',
            r'(\d+(?:\.\d+)?)\s*sft',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*mtr?s?\.?',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m\.?',
            r'(\d+(?:\.\d+)?)\s*sqft'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, dim_lower)
            if match:
                area = float(match.group(1))
                # Convert sq meters to sq feet if needed
                if 'mtr' in pattern or 'sq.m' in pattern or 'sq m' in pattern:
                    area = area * 10.764  # Convert sq meters to sq feet
                return area
        
        return None
    
    def parse_baanknet_file(self) -> List[Dict]:
        """Parse the baanknet JSON file"""
        logger.info(f"Parsing baanknet file: {self.baanknet_file}")
        
        try:
            with open(self.baanknet_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            parsed_properties = []
            for item in data:
                if item.get('status') == 1 and 'respData' in item:
                    resp_data = item['respData']
                    
                    property_data = self.unified_schema.copy()
                    property_data.update({
                        'id': item.get('property_id'),
                        'price': resp_data.get('propertyPrice'),
                        'city': resp_data.get('city'),
                        'description': resp_data.get('summaryDesc'),
                        'source': 'baanknet'
                    })
                    
                    parsed_properties.append(property_data)
            
            logger.info(f"Parsed {len(parsed_properties)} properties from baanknet file")
            return parsed_properties
            
        except Exception as e:
            logger.error(f"Error parsing baanknet file: {e}")
            return []
    
    def parse_property_details_directory(self) -> List[Dict]:
        """Parse individual JSON files from property_details directory"""
        logger.info(f"Parsing property details directory: {self.property_details_dir}")
        
        parsed_properties = []
        json_files = list(Path(self.property_details_dir).glob('*.json'))
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('success') and 'data' in data:
                    prop_data = data['data']
                    
                    property_data = self.unified_schema.copy()
                    property_data.update({
                        'id': prop_data.get('id'),
                        'borrower_name': prop_data.get('borrower_name'),
                        'bank_name': prop_data.get('bank_name'),
                        'address': prop_data.get('address'),
                        'price': prop_data.get('reserve_price'),
                        'dimensions': prop_data.get('dimensions'),
                        'area_sqft': self.extract_area_from_dimensions(prop_data.get('dimensions')),
                        'emd': prop_data.get('emd'),
                        'possession': prop_data.get('possession'),
                        'auction_date': prop_data.get('auction_date'),
                        'application_deadline': prop_data.get('application_deadline'),
                        'locality': prop_data.get('locality'),
                        'city': prop_data.get('city'),
                        'state': prop_data.get('state'),
                        'pincode': prop_data.get('pincode'),
                        'property_type': prop_data.get('property_type'),
                        'source': 'property_details'
                    })
                    
                    parsed_properties.append(property_data)
                    
            except Exception as e:
                logger.warning(f"Error parsing {file_path}: {e}")
                continue
        
        logger.info(f"Parsed {len(parsed_properties)} properties from directory")
        return parsed_properties
    
    def clean_and_standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the unified dataset"""
        logger.info("Cleaning and standardizing data")
        
        # Convert price to numeric
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Standardize city names
        df['city'] = df['city'].str.strip().str.title()
        
        # Standardize state names
        df['state'] = df['state'].str.strip().str.title()
        
        # Clean property types
        df['property_type'] = df['property_type'].str.strip().str.title()
        
        # Convert dates to datetime
        date_columns = ['auction_date', 'application_deadline']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean pincode
        df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce')
        df.loc[df['pincode'] == 0, 'pincode'] = None
        
        return df
    
    def create_unified_dataset(self) -> pd.DataFrame:
        """Main method to create unified dataset"""
        logger.info("Starting data ingestion process")
        
        # Parse both data sources
        baanknet_data = self.parse_baanknet_file()
        property_details_data = self.parse_property_details_directory()
        
        # Combine all data
        all_data = baanknet_data + property_details_data
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Clean and standardize
        df = self.clean_and_standardize(df)
        
        logger.info(f"Created unified dataset with {len(df)} properties")
        logger.info(f"Data sources: {df['source'].value_counts().to_dict()}")
        
        return df

# Usage example
if __name__ == "__main__":
    ingestion = PropertyDataIngestion(
        baanknet_file="data/baanknet_property_details.json",
        property_details_dir="data/property_details/"
    )
    
    unified_df = ingestion.create_unified_dataset()
    
    # Save to CSV
    unified_df.to_csv("unified_property_dataset.csv", index=False)
    
    # Display basic info
    print(f"Dataset shape: {unified_df.shape}")
    print(f"\nColumns: {list(unified_df.columns)}")
    print(f"\nData sources: {unified_df['source'].value_counts()}")
    print(f"\nMissing values per column:")
    print(unified_df.isnull().sum())
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

class DataProcessing():

    def __init__(self, data_path):

        self.data_path = data_path
        self.df = None

    
    def read_data(self):

        try:
            self.df = pd.read_csv(self.data_path)
        except Exception as e:
            print("Error loading csv file: ", e)
            self.df = None


    
    def geocode_addresses(self):
        """Convert UK addresses to latitude and longitude."""
        # Initialize the geocoder with a user agent (required)
        # Use UK-specific geocoder settings
        geolocator = Nominatim(user_agent="uk_roofing_company_map")
        
        # Use rate limiting to avoid being blocked
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        
        # Create empty columns for coordinates
        self.df['latitude'] = None
        self.df['longitude'] = None
        
        # Geocode each address
        for idx, row in self.df.iterrows():
            try:
                # For UK addresses, adding the country can help with geocoding accuracy
                full_address_with_country = f"{row['Address']}, UK"
                location = geocode(full_address_with_country)
                
                if location:
                    self.df.at[idx, 'latitude'] = location.latitude
                    self.df.at[idx, 'longitude'] = location.longitude
                else:
                    print(f"Could not geocode address: {row['Address']}")
                
                # Add a small delay to be nice to the geocoding service
                time.sleep(0.1)
            except Exception as e:
                print(f"Error geocoding {row['Address']}: {e}")
        
        # Remove rows with failed geocoding
        df_mapped = self.df.dropna(subset=['latitude', 'longitude'])
        print(f"Successfully geocoded {len(df_mapped)} out of {len(self.df)} addresses")
        
        return df_mapped
    

    def process_data(self):
        """Process the data and calculate average status scores per constituency"""
        self.read_data()
        geocoded_df = self.geocode_addresses()

        geocoded_df['status_str'] = geocoded_df['status'] 

        status_to_num = {
            "Stellar" : 4,
            "Good" : 3,
            "Average": 2,
            "Poor": 1,
            "None": 0,
        }
        
        # Ensure the status column is numeric
        # geocoded_df['status'] = pd.to_numeric(geocoded_df['status'], errors='coerce')
        geocoded_df['status'] = geocoded_df['status'].apply(lambda x: status_to_num[x] if x in status_to_num else None)
                                        

        
        return geocoded_df


# Data = DataProcessing('battle_ground.csv')
# Data.read_data()
# Data.geocode_addresses()
# print(Data.df.head())
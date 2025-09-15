import sys
import os
import json
from datetime import datetime

# OANDA API credentials
access_token = "89c68ff389fa5e86dd30e8aff7c8935a-b0cb097b4475427f7be111d81e76c94b"
accountID = "101-004-31569953-001"

def discover_instruments():
    """Discover available instruments from OANDA API"""
    import requests
    
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{accountID}/instruments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Categorize instruments
        commodities = []
        indices = []
        bonds = []
        forex = []
        
        for instrument in data['instruments']:
            name = instrument['name']
            display_name = instrument['displayName']
            instrument_type = instrument['type']
            
            # Check for commodities (metals, oil, etc.)
            if any(keyword in name for keyword in ['XAU', 'XAG', 'XPD', 'XPT', 'BCO', 'WTICO', 'NATGAS', 'CORN', 'SOYBN', 'WHEAT', 'SUGAR']):
                commodities.append((name, display_name, instrument_type))
            # Check for indices
            elif any(keyword in name for keyword in ['SPX500', 'NAS100', 'US30', 'UK100', 'GER30', 'JPN225', 'AUS200', 'FRA40', 'HKD33', 'DE10YB']):
                indices.append((name, display_name, instrument_type))
            # Check for bonds
            elif any(keyword in name for keyword in ['DE10YB', 'UK10YB', 'USB10Y', 'USB02Y', 'USB05Y', 'USB30Y']):
                bonds.append((name, display_name, instrument_type))
            # Everything else likely forex
            else:
                forex.append((name, display_name, instrument_type))
        
        print("=== COMMODITIES ===")
        for name, display, type_info in commodities:
            print(f"{name} - {display} ({type_info})")
        
        print("\n=== INDICES ===")
        for name, display, type_info in indices:
            print(f"{name} - {display} ({type_info})")
        
        print("\n=== BONDS ===")
        for name, display, type_info in bonds:
            print(f"{name} - {display} ({type_info})")
        
        print(f"\n=== SUMMARY ===")
        print(f"Commodities: {len(commodities)}")
        print(f"Indices: {len(indices)}")
        print(f"Bonds: {len(bonds)}")
        print(f"Forex: {len(forex)}")
        print(f"Total: {len(data['instruments'])}")
        
        # Save to file for reference
        with open('available_instruments.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nFull instrument list saved to 'available_instruments.json'")
        
        return commodities, indices, bonds
        
    except Exception as e:
        print(f"Error discovering instruments: {e}")
        return [], [], []

if __name__ == "__main__":
    discover_instruments()

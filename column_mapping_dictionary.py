# Real Estate MLS Data Column Mapping Dictionary
# Home sales data spanning 8000 days for neighborhood analysis

column_mapping = {
    # Basic Property Identifiers
    "Listing Number": "Unique MLS listing identifier",
    "Street Number": "Property street address number",
    "Street Number Modifier": "Additional street number info (e.g., 1/2, A, B)",
    "Street Direction": "Pre-directional (N, S, E, W)",
    "Street Name": "Name of the street",
    "Street Suffix": "Street type (St, Ave, Rd, etc.)",
    "Street Post Direction": "Post-directional (N, S, E, W)",
    "Unit": "Apartment/unit number if applicable",
    "City": "City where property is located",
    "State": "State abbreviation",
    "Zip Code": "Postal zip code",
    
    # Property Details
    "Area": "MLS area code/designation",
    "Subdivision": "Name of subdivision/development",
    "APN": "Assessor's Parcel Number (tax ID)",
    "Map Book": "Plat map book reference",
    "Map Page": "Plat map page reference",
    "Map X Coordinate": "X coordinate on map",
    "Map Y Coordinate": "Y coordinate on map",
    "Legal Description": "Legal property description",
    
    # Property Characteristics
    "Property Sub Type": "Type of residential property",
    "Architecture Desc": "Architectural style description",
    "Style Code": "Numeric code for architectural style",
    "Year Built": "Year property was constructed",
    "Building Condition": "Overall condition assessment",
    "Building Information": "Additional building details",
    "New Construction State": "New construction status",
    
    # Size and Layout
    "Finished Sqft": "Finished square footage",
    "Square Footage": "Total square footage",
    "Square Footage Source": "Source of square footage data",
    "Square Footage Unfinished": "Unfinished square footage",
    "Bedrooms": "Number of bedrooms",
    "Bathrooms": "Number of bathrooms",
    "Total Useable Rooms": "Total count of useable rooms",
    "Fireplaces Total": "Number of fireplaces",
    
    # Lot Information
    "Lot SqFt": "Lot size in square feet",
    "Lot Details": "Description of lot features",
    "Lot Dimensions": "Lot measurements",
    "Lot Measurement": "Unit of lot measurement",
    "Lot Number": "Lot number in subdivision",
    "Lot Topography": "Terrain description of lot",
    
    # Property Features
    "Basement": "Basement description/type",
    "Exterior": "Exterior materials/finishes",
    "Floor Covering": "Types of flooring",
    "Foundation": "Foundation type",
    "Roof": "Roofing material/type",
    "Interior Features": "Notable interior amenities",
    "Site Features": "Outdoor/site amenities",
    "View": "View description from property",
    "Waterfront": "Waterfront access (Y/N)",
    "Waterfront Footage": "Linear feet of waterfront",
    "Pool Type": "Swimming pool type if present",
    
    # Utilities and Systems
    "Energy Source": "Primary energy source",
    "Heating Cooling Type": "HVAC system type",
    "Water": "Water source type",
    "Water Company": "Water utility provider",
    "Water Heater Location": "Location of water heater",
    "Water Heater Type": "Type of water heater",
    "Sewer Type": "Sewage system type",
    "Sewer Company": "Sewer utility provider",
    "Power Company": "Electric utility provider",
    
    # Appliances and Equipment
    "Appliances That Stay": "Included appliances",
    "Leased Equipment": "Leased equipment details",
    
    # Parking and Transportation
    "Parking Type": "Type of parking available",
    "Parking Covered Total": "Number of covered parking spaces",
    "Bus Line Nearby": "Public transit access",
    
    # Manufactured Home Details (if applicable)
    "Manu. Home Manufacturer": "Mobile/manufactured home maker",
    "Manu. Home Model No.": "Mobile/manufactured home model",
    "Manu. Home Serial No.": "Mobile/manufactured home serial number",
    
    # Financial Information
    "Current Price": "Current listing price",
    "Original Price": "Original listing price",
    "Listing Price": "Listed price",
    "Selling Price": "Final sold price",
    "Taxes Annual": "Annual property taxes",
    "Association Dues": "HOA/association fees",
    "Senior Exemption": "Senior tax exemption status",
    
    # Dates and Timeline
    "Entry Date": "Date listing entered MLS",
    "Listing Date": "Date property was listed",
    "Last Price Change Date": "Date of most recent price change",
    "Pending Date": "Date property went pending",
    "Selling Date": "Date property sold",
    "Contractual Date": "Date contract was signed",
    "Contingent Date": "Date contingencies were added",
    "Inactive Date": "Date listing became inactive",
    "Status Change Date": "Date of last status change",
    "Matrix Modified DT": "Last modification date/time in MLS",
    
    # Market Metrics
    "DOM": "Days on Market",
    "CDOM": "Cumulative Days on Market",
    "Status": "Current listing status",
    
    # Agent and Office Information
    "Listing Agent ID": "Listing agent MLS ID",
    "Listing Agent Full Name": "Listing agent name",
    "Listing Agent Cellular": "Listing agent phone",
    "Co Listing Agent ID": "Co-listing agent MLS ID",
    "Co Listing Agent Full Name": "Co-listing agent name",
    "Co Listing Agent Cellular": "Co-listing agent phone",
    "Listing Office ID": "Listing office MLS ID",
    "Listing Office Name": "Listing office name",
    "Listing Office Phone": "Listing office phone",
    "Co Listing Office ID": "Co-listing office MLS ID",
    "Co Listing Office Name": "Co-listing office name",
    "Co Listing Office Phone": "Co-listing office phone",
    "Selling Agent ID": "Selling agent MLS ID",
    "Selling Agent Full Name": "Selling agent name",
    "Selling Agent Cellular": "Selling agent phone",
    "Selling Office ID": "Selling office MLS ID",
    "Selling Office Name": "Selling office name",
    "Selling Office Phone": "Selling office phone",
    
    # Property Access and Showing
    "Showing Information": "How to schedule showings",
    "Showing Instructions": "Special showing instructions",
    "Phone to Show Number": "Phone number for showings",
    "Show Addressto Public": "Whether address is public",
    "Show Map Link": "Whether to show map link",
    "Occupant Name": "Name of current occupant",
    "Occupant Type": "Type of occupancy",
    "Possession": "When possession is available",
    
    # Owner Information
    "Owner Name": "Primary owner name",
    "Owner Name 2": "Secondary owner name",
    "Owners City State": "Owner's city and state",
    
    # Financing and Terms
    "Financing": "Financing options accepted",
    "Potential Terms": "Available financing terms",
    "Bank or REO": "Bank-owned or REO status",
    "Third Party Approval Required": "Need for third-party approval",
    
    # Marketing and Media
    "Marketing Remarks": "Property description/marketing text",
    "Directions": "Driving directions to property",
    "Photo Count": "Number of listing photos",
    "Picture Provided By": "Photo source",
    "Photographer Instructions": "Instructions for photographer",
    "Virtual Tour URL": "Link to virtual tour",
    "Publish to Internet": "Whether listing is online",
    
    # Administrative
    "Agent Only Remarks": "Private remarks for agents only",
    "BBC Comments": "Broker-to-broker comments",
    "Commission": "Commission structure",
    "Preliminary Title Ordered": "Title order status",
    "Tax Year": "Property tax year",
    "County": "County where property is located",
    "School District": "School district designation",
    "Sale Type": "Type of sale transaction",
    "Building Complex Or Project Name": "Complex/project name if applicable"
}

# Additional categorizations for analysis
categorical_columns = [
    "City", "State", "Area", "Subdivision", "Property Sub Type", "Architecture Desc",
    "Building Condition", "Basement", "Exterior", "Foundation", "Roof", "Energy Source",
    "Heating Cooling Type", "Water", "Sewer Type", "Parking Type", "Status", "Occupant Type",
    "Financing", "School District", "County"
]

numerical_columns = [
    "Street Number", "Bedrooms", "Bathrooms", "Finished Sqft", "Square Footage",
    "Square Footage Unfinished", "Lot SqFt", "Fireplaces Total", "Total Useable Rooms",
    "Parking Covered Total", "Year Built", "DOM", "CDOM", "Photo Count"
]

price_columns = [
    "Current Price", "Original Price", "Listing Price", "Selling Price", "Taxes Annual",
    "Association Dues"
]

date_columns = [
    "Entry Date", "Listing Date", "Last Price Change Date", "Pending Date",
    "Selling Date", "Contractual Date", "Contingent Date", "Inactive Date",
    "Status Change Date", "Matrix Modified DT"
]

text_description_columns = [
    "Marketing Remarks", "Agent Only Remarks", "Directions", "Interior Features",
    "Site Features", "Appliances That Stay", "Floor Covering", "Lot Details"
]

print(f"Total columns mapped: {len(column_mapping)}")
print(f"Categorical columns: {len(categorical_columns)}")
print(f"Numerical columns: {len(numerical_columns)}")
print(f"Price columns: {len(price_columns)}")
print(f"Date columns: {len(date_columns)}")
print(f"Text description columns: {len(text_description_columns)}")
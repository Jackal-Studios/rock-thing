# given lat/long, fetch soil ph

# given crop input, fetch target soil ph

# given initial ph and target ph, how much lime needed? (LiTAS)

import xarray as xr
import numpy as np


def get_LR(crop, lat, long):
    # Table of crops with their target acidity saturation percentages
    crop_acidity_table = {
        "maize": 20,
        "soybean": 15,
        "wheat": 25,
        "coffee": 35,
        "rice": 25,
        "banana": 35,
        "eucalyptus": 45,
        "pine": 55,
        "sugarcane": 25,
        "cassava": 40,
        "tomato": 15,
        "tea": 30,
        "potato": 20,
        "forage grass": 35,
        "oil palm": 30
    }

    # Convert input to lowercase to handle case-insensitivity
    crop = crop.lower()


    # FETCH SOIL DATA w LAT LONG
    ECEC_i =
    ea_i =
    
    # Check if the crop exists in the table and return the corresponding target acidity saturation
    if crop in crop_acidity_table:
        lr = calculate_lr(crop_acidity_table[crop], ECEC_i, ea_i, a=0.6, b=0.92)
    else:
        raise ValueError(f"Crop '{crop}' not found. Please choose a valid crop from the list.")

    return lr

def calculate_lr(TAS, ECEC_i, ea_i, a, b):
    """
    Calculate lime requirement using LiTAS model (acid saturation approach)
    
    Parameters:
    a = cmolc of exchangeable acidity neutralized per cmolc of CaCO3
    b = 
    exch_acid_i (float): Initial exchangeable acidity [cmolc/kg]
    ECEC_i (float): Initial Effective Cation Exchange Capacity [cmolc/kg]
    TAS (float): Target Acidity Saturation [%] (default=10)
    """
    TASp = TAS/100
    LR_cmol = (ea_i - TASp * ECEC_i)/( a + TASp + (b - a) )
    return LR_cmol 


# Converts cmolc/kg to t CaCO3/ha (assuming 1.3 g/cm³ bulk density)

#fetch exch_acid_i (cmolc/kg) from soil test, effective CEC from soil test (cmolc/kg)


# given rock feedstock/biochar and lime requirement, how much feedstock needed?

# given this feedstock, how much CO2 removed? (Dietzen model)

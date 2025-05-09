

# User inputs crop, user inputs lat long, how much lime needed? (LiTAS)


import math

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
    ECEC_i = get_ECEC(lat, long)
    ea_i = get_EA(lat, long)

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



# given rock feedstock/biochar and lime requirement, how much feedstock needed?

def calculate_rock_volume(liming_rate, feedstock):
    # Hardcoded rock properties (density in kg/m³, lime equivalent in cmolc/kg)
    rock_properties = {
        "basalt": {"density": 2800, "lime_equivalence_per_kg": 0.5},
        "olivine": {"density": 3300, "lime_equivalence_per_kg": 0.6},
        # Add more rocks as needed
    }
    
    # Check if the feedstock is valid
    if feedstock not in rock_properties:
        raise ValueError(f"Feedstock '{feedstock}' not recognized. Please use a valid feedstock (e.g., basalt, olivine).")
    
    # Get the properties of the chosen feedstock
    rock_density = rock_properties[feedstock]["density"]
    lime_equivalence_per_kg = rock_properties[feedstock]["lime_equivalence_per_kg"]
    
    # Calculate how much rock mass is needed to provide the required lime (in kg)
    rock_mass_needed_kg = liming_rate / lime_equivalence_per_kg
    
    # Calculate the volume of rock required using the formula: Volume = Mass / Density
    rock_volume_needed_m3 = rock_mass_needed_kg / rock_density
    
    return rock_volume_needed_m3




# given this feedstock, how much CO2 removed? (Dietzen model)

def calculate_co2_uptake(soil_ph, pco2_uatm, cation_difference_kg_ha, temperature=15):
    """
    Calculate CO2 uptake from enhanced weathering of silicate minerals applied to soils
   
    Parameters:
    -----------
    soil_ph : float
        Soil pH measured in water (not CaCl2)
    pco2_uatm : float
        Soil CO2 partial pressure in μatm (microatmospheres)
    cation_difference_kg_ha : dict
        Dictionary containing differences in exchangeable cation content (kg/ha) between
        treated and control plots. Keys should be 'Mg', 'Ca', 'K', 'Na'
    temperature : float, optional
        Soil temperature in °C (default: 15°C)
       
    Returns:
    --------
    dict
        Dictionary containing:
        - 'x_star': Correction factor for non-carbonic acids
        - 'co2_uptake_mg': CO2 uptake for each cation in kg/ha
        - 'total_co2_uptake': Total CO2 uptake in kg/ha
    """
    import math
   
    # Convert pH to [H+] concentration
    h_plus = 10 ** (-soil_ph)
   
    # Convert pCO2 from μatm to atm and calculate [H2CO3]
    pco2_atm = pco2_uatm / 1000000
    h2co3 = pco2_atm / 29.41  # Henry's constant
   
    # Calculate K1 (equilibrium constant)
    # The paper uses K1 = 10^-6.415 at 15°C
    # This is a simplified approach; a more rigorous approach would include temperature effects
    k1 = 10 ** (-6.415)
   
    # Calculate X* correction factor (Equation 8)
    # This accounts for weathering by non-carbonic soil acids
    term1 = 10**(-20) - (10**(-10) * k1 * h2co3 / h_plus) - 10**(-10) * h_plus
    term2_inside = (10**(-10) * k1 * h2co3 / h_plus + 10**(-10) * h_plus - 10**(-20))**2
    term2_inside += 4 * 10**(-30) * k1 * h2co3 / h_plus
    term2 = math.sqrt(term2_inside)
    x_star = (term1 + term2) / (2 * 10**(-20))
   
    # Cap X* at 1.0 (it shouldn't exceed 1.0 in theory)
    x_star = min(x_star, 1.0)
   
    # Calculate CO2 uptake for each cation (Equation 9)
    co2_uptake = {}
    total_co2 = 0
   
    # Molar masses and charges of cations for calculating CO2 uptake
    cation_properties = {
        'Mg': {'charge': 2, 'atomic_mass': 24.305},
        'Ca': {'charge': 2, 'atomic_mass': 40.078},
        'K': {'charge': 1, 'atomic_mass': 39.098},
        'Na': {'charge': 1, 'atomic_mass': 22.990}
    }
   
    for cation, diff_kg_ha in cation_difference_kg_ha.items():
        if cation in cation_properties:
            # Convert cation mass to moles
            atomic_mass = cation_properties[cation]['atomic_mass']
            charge = cation_properties[cation]['charge']
           
            # Convert kg/ha to mol/ha of charge
            mol_charge_ha = (diff_kg_ha * 1000 / atomic_mass) * charge
           
            # Calculate CO2 uptake (Equation 9)
            co2_kg_ha = x_star * mol_charge_ha * 44.01 / 1000
            co2_uptake[cation] = co2_kg_ha
            total_co2 += co2_kg_ha
   
    return {
        'x_star': x_star,
        'co2_uptake_kg': co2_uptake,
        'total_co2_uptake': total_co2
    }

def calculate_co2_uptake(lr, soil_ph, pco2_uatm, depth = 0.25, lat, long):
    """
    Calculate CO2 uptake from enhanced weathering of silicate minerals applied to soils
   
    Parameters:
    -----------
    soil_ph : float
        Soil pH measured in water (not CaCl2)
    pco2_uatm : float
        Soil CO2 partial pressure in μatm (microatmospheres)
    cation_difference_kg_ha : dict
        Dictionary containing differences in exchangeable cation content (kg/ha) between
        treated and control plots. Keys should be 'Mg', 'Ca', 'K', 'Na'
    temperature : float, optional
        Soil temperature in °C (default: 15°C)
       
    Returns:
    --------
    dict
        Dictionary containing:
        - 'x_star': Correction factor for non-carbonic acids
        - 'co2_uptake_mg': CO2 uptake for each cation in kg/ha
        - 'total_co2_uptake': Total CO2 uptake in kg/ha
    """
   
    # Convert pH to [H+] concentration
    h_plus = 10 ** (-soil_ph)
   
    # Convert pCO2 from μatm to atm and calculate [H2CO3]
    pco2_atm = pco2_uatm / 1000000
    h2co3 = pco2_atm / 29.41  # Henry's constant
   
    # Calculate K1 (equilibrium constant)
    # The paper uses K1 = 10^-6.415 at 15°C
    # This is a simplified approach; a more rigorous approach would include temperature effects
    k1 = 10 ** (-6.415)
   
    # Calculate X* correction factor (Equation 8)
    # This accounts for weathering by non-carbonic soil acids
    term1 = 10**(-20) - (10**(-10) * k1 * h2co3 / h_plus) - 10**(-10) * h_plus
    term2_inside = (10**(-10) * k1 * h2co3 / h_plus + 10**(-10) * h_plus - 10**(-20))**2
    term2_inside += 4 * 10**(-30) * k1 * h2co3 / h_plus
    term2 = math.sqrt(term2_inside)
    x_star = (term1 + term2) / (2 * 10**(-20))
   
    # Cap X* at 1.0 (it shouldn't exceed 1.0 in theory)
    x_star = min(x_star, 1.0)
   
    # Calculate CO2 uptake for each cation (Equation 9)

    #add cutoff thresolds

    bulk = get_soil_bulk(lat, long)

    cat_diff = lr * bulk * depth * 100
    # Calculate CO2 uptake (Equation 9)
    co2_kg_ha = x_star * cat_diff * 44.01 / 1000
    return co2_kg_ha # kg / hectare

def get_soil_bulk(lat, long):
    return None

def get_ECEC(lat, long):
    return None

def get_EA(lat, long):
    return None
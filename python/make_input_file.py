def generate_ew_soil_file(years, feedstock, claypercent, siltpercent, temp, precip, cec, 
                          feedspread, feeddense, bulkdense, claydense, siltdense, file_num):

    mineral_rates = {
        "Basalt": -13.00,
        "HCl(c)": -10.00,
        "CO2_pump": -6.00,
        "HNO3(c)": -10.00,
        "Cs-Illite": -5.00,
        "SO4_mod_NH3": -13.0,
        "Fe(OH)3_mod_NH3": -14.144,
        "MnO2_mod_NH3": -15.2,
        "SO4_monod": -13.0,
        "Fe(OH)3_monod": -14.144,
        "Fe+++_monod": -14.144,
        "MnO2_monod": -15.2,
        "Gypsum": -6.00,
        "Calcite": -6.19,
        "Pyrite": -8.00,
        "Fe(OH)2": -7.90,
        "Fe(OH)3": -11.40,
        "FeS(am)": -8.90,
        "Vivianite": -8.0,
        "Hydroxylapatite": -11.0,
        "CARFAP": -11.0,
        "PO4ads": -11.0,
        "SiO2(am)": -11.8,
        "Katoite": -9,
        "CSH(1.8)": -9,
        "Portlandite": -9,
        "Aragonite": -8.10,
        "Dolomite": -7.70,
        "Magnesite": -9.40,
        "Siderite": -8.90,
        "CH2O_SO4": -12.40,
        "Iron": -11.30,
        "Muscovite": -13.00,
        "Quartz": -13.39,
        "Kaolinite": -13.00,
        "Ilmenite": -13.00,
        "Smectite-MgFeStef": -13.00,
        "K-Feldspar": -13.00,
        "Gibbsite": -10.00,
        "CO2(c)": -13.00,
        "Chalcedony": -13.39,
        "Ettringite": -8.00,
        "Chrysocolla": -7.00,
        "Goethite": -7.00,
        "Jarosite": -6.00,
        "Jurbanite": -6.00,
        "Alunite": -7.00,
        "Wollastonite": -13.00,
        "Larnite": -13.00
    }
    
    rate = mineral_rates.get(feedstock, None)
    # Perform calculations
    temp = temp - 273
    constant_flow = (precip / 1000) / 2
    soilclay_volfrac = (claypercent * claydense) / bulkdense
    soilsilt_volfrac = (siltpercent * siltdense) / bulkdense
    stock_volfrac = ((feedspread/10)/feeddense) / (bulkdense + ((feedspread/10)/feeddense))
    stock_clayfrac = ((claypercent * claydense) / (bulkdense + ((feedspread/10)/feeddense)))
    stock_siltfrac = ((siltpercent * siltdense) / (bulkdense + ((feedspread/10)/feeddense)))

    # Read the template file
    with open('aEWsoil.in', 'r') as file:
        content = file.read()

    # Make replacements
    content = content.replace('timeEWm.out 200', f'timeEWm{file_num}.out {years}')
    
    if feedstock != 'basalt':
        content = content.replace('An50Ab50AS', feedstock)
        content = content.replace('-rate 1.0e-13', f'-rate {rate:.2e}')
    
    content = content.replace('set_temperature 25.0', f'set_temperature {temp:.1f}')
    content = content.replace('constant_flow 0.0000158', f'constant_flow {constant_flow:.7f}')
    content = content.replace('8.9 cmol/kg', f'{cec:.1f} cmol/kg')
    
    # Replace in NativeSoil block
    native_soil_block = content.split('Condition NativeSoil')[1].split('end')[0]
    new_native_soil_block = native_soil_block.replace('Tracer', f'Tracer\n    {feedstock}')
    new_native_soil_block = new_native_soil_block.replace('Kaolinite                 0.0', f'Kaolinite                 {soilclay_volfrac:.6f}')
    new_native_soil_block += f'    K-feldspar               {soilsilt_volfrac:.6f}\n'
    content = content.replace(native_soil_block, new_native_soil_block)
    
    # Replace in Feedstock block
    feedstock_block = content.split('Condition Feedstock')[1].split('end')[0]
    new_feedstock_block = feedstock_block.replace('Tracer', f'Tracer\n    {feedstock}                  {stock_volfrac:.6f}')
    new_feedstock_block = new_feedstock_block.replace('Kaolinite                 0.0', f'Kaolinite                 {stock_clayfrac:.6f}')
    new_feedstock_block += f'    K-Feldspar               {stock_siltfrac:.6f}\n'
    content = content.replace(feedstock_block, new_feedstock_block)
    
    # Add K-Feldspar to MINERALS block
    minerals_block = content.split('MINERALS')[1].split('END')[0]
    new_minerals_block = minerals_block + 'K-Feldspar\n    -rate -13.00\n'
    content = content.replace(minerals_block, new_minerals_block)

    # Write the modified content to a new file
    with open(f'aEWsoil_{file_num}.in', 'w') as file:
        file.write(content)

    print(f"File 'aEWsoil_{file_num}.in' has been created successfully.")

    
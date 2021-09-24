def compute(rho_fat, rho_water):
    '''
    Returns the Fat Fraction ff  for values rho_fat and rho_water
    parameters: fitted parameters -> list or tuple, where rho_fat = fitted_parameters[0] and rho_water fitted_parameters[1])
    returns:    ff - > fat fraction
    '''
    return rho_fat / (rho_fat + rho_water)

    # if rho_fat / (rho_fat + rho_water) < 0.9:
    #     return rho_fat / (rho_fat + rho_water)
    # else:
    #     return 0

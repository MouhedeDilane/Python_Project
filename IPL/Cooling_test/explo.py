# Function to calculate Es based on the provided formula
def calculate_strain_energy(P1, V1, E, nu, K):
    term1 = 3 * (1 - 2 * nu) / (K ** 2)
    term2 = 2 * K ** 2 * (1 + nu)
    
    Es = (P1 ** 2 * V1 / (2 * E)) * (term1 + term2)
    
    return Es

# Parameters
P1 = 1000000  # Initial pressure in Pa
V1 = 0.02    # Internal volume of the vessel in m^3
E = 210e9    # Young's modulus in Pa (example: steel)
nu = 0.3     # Poisson's ratio (example: steel)
K = 1.5      # Ratio of the outside to inside diameter

# Calculating Es
Es = calculate_strain_energy(P1, V1, E, nu, K)

# Output the result
print(f"Strain energy (Es) in the vessel: {Es} J")
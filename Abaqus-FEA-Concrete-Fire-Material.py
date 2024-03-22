import numpy as np
import pandas as pd

Fc = 30   # Compressive Strength "MPa"
f = 0.1   # Consider Tensile Strength 10% of Compressive Strength (Applicable 6%-10%; sometimes 15%)
fe = 0.33  # Elastic Factor (Applicable range 30%-50%; sometimes 60%)
Vec = 0.18  # Poissons ratio

Tc = [20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100]  # Temperature Degree Centigrade
fc1 = [1.0, 1.0, 1.0, 1.0, 0.8486, 0.6956, 0.5426, 0.3896, 0.2366, 0.13, 0.05, 0.012]  # Compressive Strength Ratio
fc2 = [1.0, 0.896, 0.766, 0.636, 0.506, 0.376, 0.246, 0.077, 0.062, 0.046, 0.031, 0.015]  # Tensile Strength Ratio

epc = [0.0025, 0.004, 0.0055, 0.007, 0.01, 0.015, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025]  # As per EN 1991-1-2 peak strain
euc = [0.02, 0.0225, 0.025, 0.0275, 0.03, 0.0325, 0.035, 0.0375, 0.04, 0.0425, 0.045, 0.0475]  # As per EN 1991-1-2 ultimate strain

CDP_Compression = []
CDP_Tension = []
Elastic_Modulus = []

for temp, rate, peak, ultimate in zip(Tc, fc1, epc, euc):
    e = np.concatenate((np.linspace((0.5 * rate * peak * fe), peak, 6, endpoint=False),
                        np.linspace(peak, ultimate, 10)))
    St = np.concatenate(([rate * Fc * fe], rate * Fc * ((2 * (e[1:] / peak)) / (1 + (e[1:] / peak) ** 2))))
    et = np.concatenate(([0], e[1:] - ((St[1:] * peak) / (2 * Fc * rate))))
    for s, e_val in zip(St, et):
        CDP_Compression.append([s, e_val, temp])

for temp, rate, peak in zip(Tc, fc1, epc):
    Elastic_Modulus.append([((2 * Fc * rate) / (peak)), Vec, temp])

for temp, rate, rate1, peak in zip(Tc, fc2, fc1, epc):
    e = np.array([((f * Fc * rate * peak) / (2 * Fc * rate1)), 1.25 * ((f * Fc * rate * peak) / (2 * Fc * rate1)),
                  4.0 * ((f * Fc * rate * peak) / (2 * Fc * rate1)), 8.7 * ((f * Fc * rate * peak) / (2 * Fc * rate1))])
    St = np.array([f * Fc * rate, f * 0.77 * Fc * rate, f * 0.45 * Fc * rate, f * 0.1 * Fc * rate])
    et = e - ((St * peak) / (2 * Fc * rate1))
    for s, e_val in zip(St, et):
        CDP_Tension.append([s, e_val, temp])

# Create DataFrames
CDP_Compression_df = pd.DataFrame(CDP_Compression, columns=['Yield Stress (MPa)', 'Inelastic Strain', 'Temperature (°C)'])
CDP_Tension_df = pd.DataFrame(CDP_Tension, columns=['Yield Stress (MPa)', 'Cracking Strain', 'Temperature (°C)'])
Elastic_Modulus_df = pd.DataFrame(Elastic_Modulus, columns=['Young Modulus (MPa)', 'Poisson Ratio', 'Temperature (°C)'])

# Combine DataFrames horizontally
combined_df = pd.concat([CDP_Compression_df, CDP_Tension_df, Elastic_Modulus_df], axis=1)

# Write DataFrame to Excel
with pd.ExcelWriter(f'Abaqus_FEA_Fire_Material_Concrete_{Fc}_MPa.xlsx') as writer:
    combined_df.to_excel(writer, sheet_name=f'Combined_{Fc}_MPa', index=False)
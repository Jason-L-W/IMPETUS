import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv

# All functions has to do with reading and writing .csv files

#########################################################################################

# Read from .csv file
def read_csv(file_name):
    all_data = []
    try:
        with open(f"{file_name}", newline="") as csvfile:
            reader = csv.reader(csvfile)
            if reader is None: # No data
                print(f"Error: No data found in file '{file_name}'.")
                return None
            
            next(reader) # Skips Header
            for row in reader: # Read each row
                try: # Convert each value to float and append to all_data
                    all_data.append([float(v) for v in row])
                except ValueError as e:
                    print(f"Warning: Could not convert row {row} ({e})")

    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    return np.array(all_data)

#########################################################################################

# Write to .csv file
# Gets the data, points, track properties (length, height, radius), and track name and convert it into a csv
def write_csv(data, pts, prop, elementname):
    # Make the filename for CSV (function_Length_Index)
    file_name = f"{elementname}_{prop}.csv"
    # Open the file and write the following into it
    with open(file_name, mode="w", newline="") as f:
        writer = csv.writer(f)
        header = ["Index","X","Y","Z","Fx","Fy","Fz","Lx","Ly","Lz","Nx","Ny","Nz"]
        writer.writerow(header)
        writer.writerows(data)

    return file_name

#########################################################################################

# Converts txt file to csv file
def txt_to_csv(file_name):
    # Header
    h = ["Index","X","Y","Z","Fx","Fy","Fz","Lx","Ly","Lz","Nx","Ny","Nz"]

    # Replace .txt with .csv
    output_csv = file_name.rsplit('.',1)[0] + ".csv"

    try:
        df = pd.read_csv(file_name, sep="\\s+", header=None)
        df.to_csv(output_csv, index=False, header=h)
        print(f"Converted '{file_name}' to '{output_csv}'")
        return output_csv
    except Exception as e:
        print(f"Error converting file: {e}")
        return None

#########################################################################################


    
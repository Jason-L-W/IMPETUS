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
        header = ['"No."','"PosX"','"PosY"','"PosZ"','"FrontX"','"FrontY"','"FrontZ"','"LeftX"','"LeftY"','"LeftZ"','"UpX"','"UpY"','"UpZ"']
        writer.writerow(header)
        writer.writerows(data)

    return file_name

#########################################################################################

# Converts txt file to csv file
def txt_to_csv(file_name):
    # Header
    h = ['"No."','"PosX"','"PosY"','"PosZ"','"FrontX"','"FrontY"','"FrontZ"','"LeftX"','"LeftY"','"LeftZ"','"UpX"','"UpY"','"UpZ"']

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

# This actually works. DON'T TOUCH IT. If touch it may be broken.
def csv_noLimits_format(data, pts, prop, elementname):
    # NoLimits 2 spline header format
    file_name = f"{elementname}_{prop}.csv"
    
    # Define the precise NoLimits 2 spline header with literal tab spacing
    header_line = '"No."\t"PosX"\t"PosY"\t"PosZ"\t"FrontX"\t"FrontY"\t"FrontZ"\t"LeftX"\t"LeftY"\t"LeftZ"\t"UpX"\t"UpY"\t"UpZ"\n'
    
    # Open the file and write out directly
    with open(file_name, mode="w", newline="", encoding="utf-8") as f:
        # 1. Write the header line cleanly with zero backslashes
        f.write(header_line)
        
        # 2. Iterate through the array slices and format each item into scientific notation
        for row in data[:pts]:
            # Element 0 is the index integer, the rest (1 to 12) are float coordinates/vectors
            idx = int(row[0])
            coords = row[1:13]
            
            # Convert float items to scientific notation strings (e.g., 1.234560e+01)
            # %e provides standard scientific notation format matching MATLAB's %e behavior
            formatted_coords = [f"{float(val):e}" for val in coords]
            
            # Combine the integer index with the formatted float coordinates
            line_items = [str(idx)] + formatted_coords
            
            # Join together with tabs and write the line
            f.write("\t".join(line_items) + "\n")

    print(f"file {file_name} created successfully")
    return file_name
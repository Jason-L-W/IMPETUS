import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv

# Folder creation
def initalize_folders(section_folder):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    cwd = os.getcwd()
    if os.path.basename(cwd) == "IMPETUS":
        base_dir = cwd
    else:
        base_dir = current_dir
        while os.path.basename(base_dir) != "IMPETUS" and os.path.dirname(base_dir) != base_dir:
            base_dir = os.path.dirname(base_dir)

        if os.path.basename(base_dir) != "IMPETUS":
            base_dir = cwd

    master_folder = os.path.join(base_dir, section_folder)

    subfolders = {
        "master": master_folder,
        "images": os.path.join(master_folder, "Images"),
        "coaster": os.path.join(master_folder, "Coasters"),
    }

    for folder in subfolders.values():
        os.makedirs(folder, exist_ok=True)


# All functions HERE has to do with file manipulation.
# ========================================================================
#                           Read from .csv files
# ========================================================================
def read_csv(file_name):
    all_data = []
    try:
        with open(f"Prebuilt_tracks/{file_name}", "r", newline="", encoding="utf-8") as csvfile:
            # Peek at the first line to detect the delimiter
            first_line = csvfile.readline()
            if not first_line.strip(): 
                print(f"Error: No data found in file '{file_name}'.")
                return None
            
            # Reset file pointer back to the beginning
            csvfile.seek(0) 
            
            # Dynamically choose parser based on whether a comma is present
            if ',' in first_line:
                reader = csv.reader(csvfile, delimiter=',')
            else:
                # Custom generator to handle arbitrary spaces/tabs smoothly
                reader = (line.split() for line in csvfile)
            
            # Skip Header
            next(reader) 
            
            # Read each row
            for row in reader: 
                if not row:  # Skip empty rows
                    continue
                try: 
                    # Convert values to float (stripping quotes just in case)
                    all_data.append([float(v.strip('"\'')) for v in row])
                except ValueError as e:
                    print(f"Warning: Could not convert row {row} ({e})")

    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    return np.array(all_data)


# ========================================================================
#                           Write to .csv files
# ========================================================================
# Gets the data, points, track properties (length, height, radius), and track name and convert it into a csv
def write_csv(data, pts, prop, elementname):
    # Make the filename for CSV (function_Length_Index)
    file_name = f"Segments/{elementname}_{prop}.csv"
    # Open the file and write the following into it
    with open(file_name, mode="w", newline="") as f:
        writer = csv.writer(f)
        header = ['"No."','"PosX"','"PosY"','"PosZ"','"FrontX"','"FrontY"','"FrontZ"','"LeftX"','"LeftY"','"LeftZ"','"UpX"','"UpY"','"UpZ"']
        writer.writerow(header)
        writer.writerows(data)

    return None


# ========================================================================
#                           Generate .svg files
# ========================================================================
def export_layouts(section_folder, track_data, xy_composition, track_plots):
    X, Y, Z, *unused_data = track_data
    font_size, cushion = 8, 5

    x_min_top, x_max_top = np.min(X), np.max(X)
    z_min_top, z_max_top = np.min(Z), np.max(Z)
    top_view_x_span = x_max_top - x_min_top
    top_view_y_span = z_max_top - z_min_top

    # Used to find the boundaries of each segment
    segment_boundaries = calculate_segment_boundaries(xy_composition)

    # Build the combined subplots matrix
    fig, axes = plt.subplots(4, 1, figsize=(24, 48))
    combined_configs = [
        {"title": "Whole Track Top View", "type": "top"},
        {"title": "Section 1-2",           "type": "sec_12"},
        {"title": "Section 3",             "type": "sec_3"},
        {"title": "Section 4-5",           "type": "sec_45"}
    ]
    
    # Exports a
    combined_view(axes, combined_configs, xy_composition, segment_boundaries, X, Z)

    # 3. Export standalone views with temporary context decorations
    export_individual_views(section_folder, track_plots, segment_boundaries, font_size)

    # 4. Format combined axes, split if necessary, and save print layout components
    export_printed_pieces(section_folder, axes, combined_configs, xy_composition, X, Z, cushion, top_view_y_span, x_min_top, x_max_top, z_min_top, z_max_top)

    # Final combined save
    fig.subplots_adjust(left=1.0/24.0, right=1.0-(1.0/24.0), bottom=1.0/12.0, top=1.0-(1.0/12.0))
    fig.savefig(f"{section_folder}/Images/combined_track_views.svg", dpi=300)
    plt.close(fig)


# === Finds the segment boundaries
def calculate_segment_boundaries(xy_composition):
    segment_boundaries = {}
    current_horizontal_offset = 0
    
    # Find the start and end of each track segment
    for idx, segment in enumerate(xy_composition):
        local_horizontal = segment["XY"]
        global_2d_horizontal = local_horizontal + current_horizontal_offset
        segment_boundaries[idx] = {
            "start_x": global_2d_horizontal[0],
            "end_x": global_2d_horizontal[-1],
        }
        current_horizontal_offset = global_2d_horizontal[-1]
    return segment_boundaries

# === Display the top view and all sideview compoenents to scale with the top view ===
def combined_view(axes, combined_configs, xy_composition, segment_boundaries, X, Z):
    section_colors = {
        "sec_1": "#1f77b4",
        "sec_2": "#ff7f0e",
        "sec_3": "#2ca02c", 
        "sec_4": "#c13017",
        "sec_5": "#1725c1"
    }
    
    axes[0].plot(0, 0, color='black', marker='o', markersize=6, zorder=5)
    current_horizontal_offset = 0
    array_idx_start = 0

    for idx, segment in enumerate(xy_composition):
        local_horizontal = segment["XY"]
        Z_elevation = segment["Z"]
        global_2d_horizontal = local_horizontal + current_horizontal_offset
        segment_color = section_colors.get(f"sec_{idx+1}", "gray")
        array_idx_end = array_idx_start + len(local_horizontal)
        
        # Plot top view
        axes[0].plot(X[array_idx_start:array_idx_end], Z[array_idx_start:array_idx_end], color=segment_color, linewidth=2)
        if idx < len(xy_composition) - 1:
            transition_idx = min(array_idx_end - 1, len(X) - 1)
            axes[0].plot(X[transition_idx], Z[transition_idx], color='black', marker='o', markersize=6, zorder=5)

        # Plot side views
        for ax_idx, config in enumerate(combined_configs[1:], start=1):
            plot_type = config["type"]
            is_in_this_row = (
                (plot_type == "sec_12" and idx in (0, 1)) or
                (plot_type == "sec_3"  and idx == 2) or
                (plot_type == "sec_45" and idx in (3, 4))
            )
            if is_in_this_row:
                row_start_offset = (segment_boundaries[0]["start_x"] if idx in (0, 1) else 
                                    segment_boundaries[2]["start_x"] if idx == 2 else 
                                    segment_boundaries[3]["start_x"])
                axes[ax_idx].plot(global_2d_horizontal - row_start_offset, Z_elevation, color=segment_color, linewidth=2)

        array_idx_start = array_idx_end - 1
        current_horizontal_offset = global_2d_horizontal[-1]


def export_individual_views(section_folder, track_plots, segment_boundaries, font_size):
    """Decorates, saves, and reverts isolated view plots from track_plots dict."""
    view_configs = [
        ("whole_track_topview",  "Whole Track Topview"),
        ("whole_track_sideview", "Whole Track Sideview"),
        ("section_12",           "Section 1-2"),
        ("section_3",            "Section 3"),
        ("section_45",           "Section 4-5")
    ]

    for key, title in view_configs:
        if key not in track_plots:
            continue
            
        ax = track_plots[key]["ax"]
        filename = f"{title.lower().replace(' ', '_')}.svg"
        temp_elements = []

        # If its the whole track sideview, plot with guidelines below the track
        if key == "whole_track_sideview":
            y_min, y_max = ax.get_ylim()
            padding = (y_max - y_min) * 0.8
            new_y_min = y_min - padding
            ax.set_ylim(bottom=new_y_min)

            canvas_floor_y = new_y_min
            upper_hline_y = new_y_min + (padding * 0.85)
            lower_hline_y = new_y_min + (padding * 0.35)
            label_y = new_y_min + (padding * 0.60)

            global_start_x = segment_boundaries[0]["start_x"]
            global_end_x = segment_boundaries[max(segment_boundaries.keys())]["end_x"]

            temp_elements.append(ax.plot([global_start_x, global_end_x], [upper_hline_y, upper_hline_y], color='red', linestyle='-', linewidth=0.6, zorder=1)[0])
            temp_elements.append(ax.plot([global_start_x, global_end_x], [lower_hline_y, lower_hline_y], color='blue', linestyle='-', linewidth=0.6, zorder=1)[0])
            temp_elements.append(ax.plot([global_start_x, global_start_x], [canvas_floor_y, upper_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=1)[0])
            temp_elements.append(ax.plot([global_end_x, global_end_x], [canvas_floor_y, upper_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=1)[0])

            for s_idx, bounds in segment_boundaries.items():
                mid_x_loc = (bounds["start_x"] + bounds["end_x"]) / 2.0
                section_name = ax.text(x=mid_x_loc, y=label_y, s=f"Section {s_idx+1}", fontsize=font_size * 0.6, color='black', ha='center', va='center')
                temp_elements.append(section_name)

                if s_idx < len(segment_boundaries) - 1:
                    sub_vline, = ax.plot([bounds["end_x"], bounds["end_x"]], [canvas_floor_y, lower_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=2)
                    temp_elements.append(sub_vline)

        ax.axis('off')
        ax.set_title(title, fontsize=font_size)
        ax.figure.savefig(f"{section_folder}/Images/{filename}", dpi=300)
        ax.axis('on')

        # Clean up temporary layout lines
        for element in temp_elements:
            element.remove()
        if key == "whole_track_sideview":
            try:
                ax.set_ylim(y_min, y_max)
            except NameError:
                pass


def export_printed_pieces(section_folder, axes, combined_configs, xy_composition, X, Z, cushion, top_view_y_span, x_min_top, x_max_top, z_min_top, z_max_top):
    """Processes scaling, adds tooth baselines, and cuts ultra-wide plots into printable chunks."""
    for ax_idx, config in enumerate(combined_configs):
        ax = axes[ax_idx]
        plot_type = config["type"]
        
        if plot_type == "top":
            ax.plot(x_min_top, 0, 'go', markersize=8)
            ax.plot(x_max_top, 0, 'go', markersize=8)
            ax.set_xlim(x_min_top - cushion, x_max_top + cushion)
            ax.set_ylim(z_min_top - cushion, z_max_top + cushion)
        else:
            lines = ax.get_lines()
            y_base = min([np.min(l.get_ydata()) for l in lines] + [np.max(l.get_ydata()) for l in lines]) if lines else 0
            ax.set_xlim(x_min_top - cushion, x_max_top + cushion)
            ax.set_ylim(y_base - cushion, y_base + top_view_y_span + cushion)
        
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')

        current_xlim = ax.get_xlim()
        track_x_data, track_y_data = [], []
        for line in ax.get_lines():
            track_x_data.extend(line.get_xdata())
            track_y_data.extend(line.get_ydata())
        track_x_data, track_y_data = np.array(track_x_data, dtype=float), np.array(track_y_data, dtype=float)

        box_physical_width_inches = 22.0
        box_data_width = float(current_xlim[1] - current_xlim[0])
        one_inch_in_data_units = box_data_width / box_physical_width_inches
            
        t_min_x = float(np.min(track_x_data)) if track_x_data.size > 0 else 0.0
        t_max_x = float(np.max(track_x_data)) if track_x_data.size > 0 else 1.0
        actual_track_span = t_max_x - t_min_x

        should_split = (plot_type != "top") and (actual_track_span > (box_physical_width_inches * one_inch_in_data_units))
        split_passes = ["piece_A", "piece_B"] if should_split else ["full"]
        midpoint_x = (t_min_x + t_max_x) / 2.0
        
        for pass_type in split_passes:
            single_fig = plt.figure(figsize=(24, 12))
            single_ax = single_fig.add_axes([1.0/24.0, 1.0/12.0, (24.0-2.0)/24.0, (12.0-2.0)/12.0])
        
            for line in ax.get_lines():
                lx, ly = line.get_xdata(), line.get_ydata()
                if pass_type == "piece_A":
                    mask = lx <= midpoint_x
                    if np.any(mask): single_ax.plot(lx[mask], ly[mask], color=line.get_color(), linewidth=line.get_linewidth())
                elif pass_type == "piece_B":
                    mask = lx >= midpoint_x
                    if np.any(mask): single_ax.plot(lx[mask] - (midpoint_x - t_min_x), ly[mask], color=line.get_color(), linewidth=line.get_linewidth())
                else:
                    single_ax.plot(lx, ly, color=line.get_color(), linewidth=line.get_linewidth())

            if plot_type == "top":
                dot_array_idx = 0
                for segment in xy_composition[:-1]:
                    dot_array_idx += len(segment["XY"]) - 1
                    single_ax.plot(X[dot_array_idx], Z[dot_array_idx], color='black', marker='o', markersize=6, zorder=5)

            # Add the greek keys to the sideviews
            x_pattern, y_pattern = [], []
            if plot_type != "top":
                step_size = 0.5 * one_inch_in_data_units  
                tooth_height = 0.5 * one_inch_in_data_units
                lowest_point = float(np.min(track_y_data)) if len(track_y_data) > 0 else 0.0
                highest_point = float(np.max(track_y_data)) if len(track_y_data) > 0 else 10.0
                
                y_baseline = lowest_point - (one_inch_in_data_units * 2.0)
                y_top_limit = highest_point + (one_inch_in_data_units * 1.5)

                p_min_x, p_max_x = (t_min_x, midpoint_x) if pass_type == "piece_A" else (t_min_x, t_max_x - (midpoint_x - t_min_x)) if pass_type == "piece_B" else (t_min_x, t_max_x)


                num_cycles = int((p_max_x - p_min_x) / (step_size * 2)) + 1
                current_x = p_min_x

                x_pattern.append(current_x)
                y_pattern.append(y_baseline)
                for _ in range(num_cycles):
                    tooth_top = min(y_baseline + tooth_height, -(one_inch_in_data_units * 0.2))
                    x_pattern.extend([current_x, current_x, current_x + step_size, current_x + step_size, current_x + step_size])
                    y_pattern.extend([tooth_top, y_baseline, y_baseline, y_baseline, tooth_top])
                    current_x += (step_size * 2)
                
                single_ax.plot(np.array(x_pattern, dtype=float), np.array(y_pattern, dtype=float), color='black', linewidth=1, zorder=1)
                # Vertical lines are the beginning and end (Used for Cricut)
                single_ax.plot([p_min_x, p_min_x], [y_baseline, y_top_limit], color='black', linewidth=1)
                single_ax.plot([p_max_x, p_max_x], [y_baseline, y_top_limit], color='black', linewidth=1)

                if pass_type == "piece_A":
                    single_ax.plot([midpoint_x, midpoint_x], [y_baseline, y_top_limit], color='black', linewidth=1)
                elif pass_type == "piece_B":
                    single_ax.plot([t_min_x, t_min_x], [y_baseline, y_top_limit], color='black', linewidth=1)

                single_ax.set_ylim(y_baseline - (one_inch_in_data_units * 0.5), y_top_limit)
            else:
                single_ax.set_ylim(ax.get_ylim())

            data_min_x = t_min_x if pass_type in ["piece_A", "piece_B"] else np.min(track_x_data) if track_x_data.size > 0 else current_xlim[0]
            data_max_x = midpoint_x if pass_type == "piece_A" else t_max_x - (midpoint_x - t_min_x) if pass_type == "piece_B" else np.max(track_x_data) if track_x_data.size > 0 else current_xlim[1]

            if plot_type != "top" and x_pattern:
                data_min_x, data_max_x = min(data_min_x, np.min(x_pattern)), max(data_max_x, np.max(x_pattern))
                
            data_mid_x = (data_min_x + data_max_x) / 2.0
            half_width = (current_xlim[1] - current_xlim[0]) / 2.0
            single_ax.set_xlim(data_mid_x - half_width, data_mid_x + half_width)
            single_ax.set_aspect('equal', adjustable='box')
            single_ax.axis('off')
            
            safe_title = config["title"].lower().replace(' ', '_').replace('-', '_')
            suffix = f"_{pass_type}" if should_split else ""
            single_fig.savefig(f"{section_folder}/Images/to_print_{safe_title}{suffix}.svg", dpi=300, transparent=True, facecolor='none', pad_inches=0)
            plt.close(single_fig)

# ========================================================================
#                       NoLimits 2 Spline Format
# ========================================================================
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
            formatted_coords = [f"{float(val):e}" for val in coords]
            
            # Combine the integer index with the formatted float coordinates
            line_items = [str(idx)] + formatted_coords
            
            # Join together with tabs and write the line
            f.write("\t".join(line_items) + "\n")

    print(f"file {file_name} created successfully")
    return None


if __name__ == "__main__":
    # initalize_folders("Test_Section_123")
    pass
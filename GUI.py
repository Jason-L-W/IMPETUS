import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QLineEdit,
    QSpacerItem, QSizePolicy, QStackedWidget,
    QTabWidget, QFormLayout, QSlider, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator
from matplotlib.figure import Figure
import numpy as np

import tracks

# When adding new track types, they should be added to the ALL_TRACKS list and the track_function_map dictionary below.

# ========================================================================
SECTIONS = ["Starts", "Thrills 1", "Turns", "Thrills 2", "Ends"]    # Defines the sections of the track assembly
STARTS = ["Launcher", "Lift Hill", "Rollback"]                      # Defines the starting track types
THRILLS = ["Loop", "Camelback", "Corkscrew"]                        # Defines the thrill track types
TURNS = ["Cobral Roll", "Horseshoe", "Helix"]                       # Defines the turn track types
ENDS = ["Brake", "Rollup"]                                          # Defines the ending track types
ALL_TRACKS = STARTS + THRILLS + TURNS + ENDS                        # Defines all track types for validation
# ========================================================================

# Maps track types to their corresponding functions in the tracks module.
# When there are new track types, they should be added to this dictionary with their corresponding function from the tracks module.
track_function_map = {
    # Starts
    "Launcher": tracks.TrackPart.launcher_func,             # Using this will result a return to the beginning of the track
    "Lift Hill": tracks.TrackPart.lifthill_func,            # Using this will result a return to the beginning of the track
    "Rollback": tracks.TrackPart.rollback_func,             # Has no return, but can be used to begin the track with a rollback

    # Thrills
    "Loop": tracks.TrackPart.loopCG_func,
    "Camelback": tracks.TrackPart.camelback_func,
    "Corkscrew": tracks.TrackPart.corkscrew_func,

    # Turns
    "Cobral Roll": tracks.TrackPart.cobrarollCG_func,
    "Horseshoe": tracks.TrackPart.horseshoe_func,
    "Helix": tracks.TrackPart.helix_func,

    # Ends
    "Brake": tracks.TrackPart.brake_func,                   # Using this will result a return to the beginning of the track
    "Rollup": tracks.TrackPart.rollup_func               # Has no return, but can be used to end the track with a rollup

}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track RollerCoaster")
        self.setGeometry(100, 100, 1000, 680)

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Title
        title = QLabel("IMPETUS Roller Coaster Track Builder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 10px; background-color: #34495e; border-radius: 10px;")
        title.setFixedHeight(60)
        self.layout.addWidget(title)

        # Track Panel (Assembly and Visualization)
        self.track_widget = QWidget()
        self.track_widget.setStyleSheet("background-color: green; border-radius: 10px; padding: 10px;")
        self.track_layout = QHBoxLayout(self.track_widget)

        # Assembly structures setup ahead of panel assignments
        self.section_layouts = {}
        self.tracks = {section: [] for section in SECTIONS}

        # Assembly and Visual Panels
        self.assembly_panel()
        self.visual_panel()
        self.layout.addWidget(self.track_widget)
        self.create_button()

        # Setup the track assembly sections (Initialize each section)
        for section in SECTIONS:
            self.track_type(section)
        self.switch_view_mode(0)


    # ========================================================================
    #                       Assembly Panels and Controls
    # ========================================================================
    def assembly_panel(self):
        self.assembly_widget = QWidget()
        self.assembly_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; padding: 0px;")
        self.assembly_layout = QVBoxLayout(self.assembly_widget)

        track_assembly_label = QLabel("Track Assembly")
        track_assembly_label.setStyleSheet("color: blue; font-size: 20px; background-color: white; padding: 5px; border-radius: 5px;")
        track_assembly_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        track_assembly_label.setFixedHeight(40)
        self.assembly_layout.addWidget(track_assembly_label)

        # Setup Mode Selector (Dropdown to switch between single page and tabbed view)
        selector_layout = QHBoxLayout()
        selector_label = QLabel("View Mode: ")
        selector_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

        self.setup_selector = QComboBox()
        self.setup_selector.addItems(["Setup 1: All on 1 Page", "Setup 2: Tabbed View"])
        self.setup_selector.setStyleSheet("""
            QComboBox { background-color: white; color: #2c3e50; padding: 6px; border-radius: 5px; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: white; border-radius: 5px; font-weight: bold; }
                                          """)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.setup_selector)
        self.assembly_layout.addLayout(selector_layout)

        self.assembly_stack = QStackedWidget()
        self.assembly_layout.addWidget(self.assembly_stack)

        self.single_page_view() # Setup 1: All on 1 page
        self.tabbed_view()      # Setup 2: Multiple pages

        self.setup_selector.currentIndexChanged.connect(self.switch_view_mode)

        # Add to the main layout, with a scale factor of 1 to make it smaller
        self.track_layout.addWidget(self.assembly_widget, 1)
        

    # ========================================================================
    #                       Visual Panels and Controls
    # ========================================================================
    def visual_panel(self):
        # Visual Widget
        self.visual_widget = QWidget()
        self.visual_widget.setStyleSheet("background-color: #bdc3c7; border-radius: 10px; padding: 10px;")
        visual_layout = QVBoxLayout(self.visual_widget)

        # Visual Label
        visual_label = QLabel("Track Visualization")
        visual_label.setStyleSheet(
            "color: blue; font-size: 20px; background-color: white;"
            "padding: 5px; border-radius: 5px;"
        )
        visual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        visual_label.setFixedHeight(40)
        visual_layout.addWidget(visual_label)

        # Visual Stack (Placeholder and Tab Widget)
        self.visual_constent_layout = QVBoxLayout()
        visual_layout.addLayout(self.visual_constent_layout)

        # Placeholder Label (Inital State)
        self.placeholder_label = QLabel("Track visualization will appear here after assembly.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #7f8c8d; font-size: 16px;")
        self.placeholder_label.setWordWrap(True)
        self.visual_constent_layout.addWidget(self.placeholder_label)

        # Inital Tab Widget (Hidden until assembly is complete)
        self.visual_tab_widget = QTabWidget()
        self.visual_tab_widget.setStyleSheet("background-color: white; color: black; font-weight: bold;")
        self.visual_tab_widget.hide()
        self.visual_constent_layout.addWidget(self.visual_tab_widget)

        # Keep track of the plots
        self.track_plots = {}

        # === Tab 1: 3D Visualization ===
        fig_3d = Figure(layout="constrained")  # Use constrained layout for better spacing
        canvas_3d = FigureCanvas(fig_3d)
        ax_3d = fig_3d.add_subplot(111, projection='3d')

        self.track_plots["3d"] = {
            "figure": fig_3d,
            "canvas": canvas_3d,
            "ax": ax_3d
        }
        
        tab_3d_page = QWidget()
        tab_3d_layout = QVBoxLayout(tab_3d_page)
        tab_3d_layout.setContentsMargins(0, 0, 0, 0)
        tab_3d_layout.addWidget(canvas_3d)
        self.visual_tab_widget.addTab(tab_3d_page, "3D View")

        # === Rest of the Tab: 2D Visualization ===
        tabs_2d = [
            ("whole_track_topview", "2D View (Whole Track Top View)"),
            ("whole_track_sideview", "2D View (Whole Track Side View)"),
            ("section_12", "2D View (Sections 1/2)"),
            ("section_3", "2D View (Sections 3)"),
            ("section_45", "2D View (Sections 45)")
        ]

        for key, tab_title in tabs_2d:
            # Creating the Matplotlib objects
            fig = Figure()
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            self.track_plots[key] = {
                "figure": fig,
                "canvas": canvas,
                "ax": ax
            }
            
            # Add to the tab widget
            self.visual_tab_widget.addTab(canvas, tab_title)

        # Add to the main layout, with a scale factor of 3 to make it larger
        self.track_layout.addWidget(self.visual_widget, 3)


    # ========================================================================
    #                           Create Button
    # ========================================================================
    def create_button(self):
        self.create_button = QPushButton("Create")
        self.create_button.setStyleSheet(
            "background-color: #2ecc71; color: white; font-size: 18px;"
            "padding: 10px; border-radius: 10px;"
        )
        self.create_button.clicked.connect(self.start_generating)
        self.layout.addWidget(self.create_button)      


    # ========================================================================
    #                       Assembly Helper Functions
    # ========================================================================
    def single_page_view(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent; font-size: 12px; font-weight: bold;")
        
        self.single_page_widget = QWidget()
        self.single_page_widget.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; padding: 10px;")
        self.single_page_main_layout = QVBoxLayout(self.single_page_widget)
        self.single_page_main_layout.setContentsMargins(5, 5, 5, 5)
        self.single_page_main_layout.setSpacing(10)

        self.single_page_cards_layouts = {}
        self.single_page_cards = {}
        for section in SECTIONS:
            card = QWidget()
            card.setStyleSheet("background-color: #ffffff; border-radius: 10px; margin-bottom: 2px; padding: 2px;")
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(2)
            
            title = QLabel(f"[{section}]")
            title.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 14px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(title)
            
            self.single_page_cards_layouts[section] = card_layout
            self.single_page_cards[section] = card
            self.single_page_main_layout.addWidget(card)
            
        self.single_page_main_layout.addStretch()
        scroll_area.setWidget(self.single_page_widget)
        self.assembly_stack.addWidget(scroll_area)

    def tabbed_view(self):
        self.assembly_tabs = QTabWidget()
        self.assembly_tabs.setStyleSheet("""
            QTabWidget::panel {background-color: #ecf0f1; border-radius: 10px; padding: 10px; font-weight: bold;}
            QTabBar::tab {background-color: #2c3e50; color: white; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-weight: bold;}
            QTabBar::tab:selected {background-color: #ffffff; color: #2c3e50; font-weight: bold;}
        """)

        self.tab_layouts = {}
        self.tab_widgets = {}
        for section in SECTIONS:
            tab_widget = QWidget()
            tab_widget.setStyleSheet("background-color: #ffffff; border-radius: 10px; border-top-left-radius: 0px; padding: 10px; font-weight: bold;")
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(5, 5, 5, 5)
            
            self.tab_layouts[section] = tab_layout
            self.tab_widgets[section] = tab_widget
            self.assembly_tabs.addTab(tab_widget, section)
            
        self.assembly_stack.addWidget(self.assembly_tabs)

    def switch_view_mode(self, index):
        # The default is all on 1 page, but can change between them if the user wants

        for section in SECTIONS:
            if index == 0:
                target_layout = self.single_page_cards_layouts[section]
            else:
                target_layout = self.tab_layouts[section]
                
            # Re-setup the layout
            for widget in self.tracks[section]:
                widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                target_layout.addWidget(widget)

        # Flip the visible stack page
        self.assembly_stack.setCurrentIndex(index)

    def track_type(self, section):        
        # Veritcal Dropdown Widget (Selecting Track Type)
        col_widget = QWidget()
        col_layout = QVBoxLayout(col_widget)
        track_dropdown = QComboBox()
        track_dropdown.setPlaceholderText("Select Track Type")

        if section == "Starts":
            track_dropdown.addItems(STARTS)
        elif section == "Thrills 1" or section == "Thrills 2":
            track_dropdown.addItems(THRILLS)
        elif section == "Turns":
            track_dropdown.addItems(TURNS)
        elif section == "Ends":
            track_dropdown.addItems(ENDS)
        
        # Setup the Length Input Field
        length_input = QLineEdit()
        length_input.setPlaceholderText("Track Length")
        # ======= Test Value =======
        length_input.setText("11")
        # ==========================

        # Setup the Slider
        length_slider = QSlider(Qt.Orientation.Horizontal)
        length_slider.setRange(1, 100)
        # ======= Test Value =======
        length_slider.setValue(11)
        # ==========================
        
        # Connects Slider to Line Input Field (Moving the slider updates the text)
        length_slider.valueChanged.connect(lambda value: length_input.setText(str(value)))

        # Connects Line Input Field to Slider (Changing input value changes the slider position)
        def sync_slider_from_text(text):
            # Skip validation if box is empty
            if not text:
                return

            try:
                val = int(text)
                # Makes sure that if the input value is not within the set range
                if length_slider.minimum() <= val <= length_slider.maximum():
                    length_slider.blockSignals(True)
                    length_slider.setValue(val)
                    length_slider.blockSignals(False)

                # If not throws an error message
                elif val < length_slider.minimum() or val > length_slider.maximum():
                    QMessageBox.warning(
                        self,
                        "Invalid Number",
                        f"Track length must be within the range of {length_slider.minimum()} - {length_slider.maximum()}"
                    )

            except ValueError:
                pass

        length_input.textChanged.connect(sync_slider_from_text)

        # Add the widgets to the row layout
        col_layout.addWidget(track_dropdown)
        col_layout.addWidget(length_input)
        col_layout.addWidget(length_slider)

        self.tracks[section].append(col_widget)


    # ========================================================================
    #                       Visual Helper Functions
    # ========================================================================
    def update_visual(self, track_data, xy_composition):
        self.placeholder_label.hide()  # Hide the placeholder label
        self.visual_tab_widget.show()  # Show the visual widget

        X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = track_data
        font_size = 8
        grid_padding = 5

        for plot in self.track_plots.values():
            plot["ax"].clear()

        # === 3D View ===
        # This might look weird, but the axes are swapped to make the visualization more intuitive (X, Z, Y) instead of (X, Y, Z).
        # Right hand rule is used to determine the orientation of the axes, and this swap makes it easier to visualize the track in a more natural way.
        # X is the forward direction axis, Y is the left direction axis, and Z is the upward direction axis.
        ax3d = self.track_plots["3d"]["ax"]
        canvas_3d = self.track_plots["3d"]["canvas"]
        ax3d.plot3D(X, Z, Y, 'b-', label='Track Path')
        ax3d.plot3D(X + Nx, Z + Nz, Y + Ny, 'r-', alpha=0.4, label='Normals')
        ax3d.set_xlabel("X", fontsize=font_size)
        ax3d.set_ylabel("Y", fontsize=font_size)
        ax3d.set_zlabel("Z", fontsize=font_size)
        ax3d.tick_params(axis='both', which='major', labelsize=font_size - 2)
        ax3d.tick_params(axis='both', which='minor', labelsize=font_size - 4)
        
        # Scale the 3D plot to fit the data better (A 1:1:1 aspect ratio for better visualization)
        x_range = np.max(X) - np.min(X)
        y_range = np.max(Y) - np.min(Y)
        z_range = np.max(Z) - np.min(Z)
        max_range = max(x_range, y_range, z_range)
        box_x = x_range / max_range
        box_y = y_range / max_range
        box_z = z_range / max_range
        ax3d.set_box_aspect((box_x, box_z, box_y))  # Adjust aspect ratio for better visualization

        ax3d.set_xlim(np.min(X) - grid_padding, np.max(X) + grid_padding)
        ax3d.set_ylim(np.min(Z) - grid_padding, np.max(Z)+ grid_padding)
        ax3d.set_zlim(np.min(Y) - grid_padding, np.max(Y) + grid_padding)

        ax3d.legend(loc='upper right', bbox_to_anchor=(1.0, 1.0), fontsize=font_size)
        canvas_3d.draw()

        # === 2D View ===
        # Plotting the Top View
        self.track_plots["whole_track_topview"]["ax"].plot(X, Z)

        # Plotting the Side View (XY Composition of the Tracks)
        segment_boundaries = {}
        current_horizontal_offset = 0
        for idx, segment in enumerate(xy_composition):
            local_horizontal = segment["XY"]
            Z_elevation = segment["Z"]
            global_2d_horizontal = local_horizontal + current_horizontal_offset
            
            self.track_plots["whole_track_sideview"]["ax"].plot(global_2d_horizontal, Z_elevation)

            segment_boundaries[idx] = {
                "start_x": global_2d_horizontal[0],
                "end_x": global_2d_horizontal[-1],
            }

            # Also plot the whole track into 3 different sections
            if idx in (0, 1):
                self.track_plots["section_12"]["ax"].plot(global_2d_horizontal, Z_elevation)
            elif idx == 2:
                self.track_plots["section_3"]["ax"].plot(global_2d_horizontal, Z_elevation)
            elif idx in (3, 4):
                self.track_plots["section_45"]["ax"].plot(global_2d_horizontal, Z_elevation)

            current_horizontal_offset = global_2d_horizontal[-1]  # Update the offset for the next segment

        # 2D View Settings
        view_configs = [
            ("whole_track_topview",     "Whole Track Top View",     "X",    "Y"),
            ("whole_track_sideview",    "Whole Track Side View",    "XY",   "Z"),
            ("section_12",              "Section 1-2",              "XY",   "Z"),
            ("section_3",               "Section 3",                "XY",   "Z"),
            ("section_45",              "Section 4-5",              "XY",   "Z")
        ]

        for key, title, xlabel, ylabel in view_configs:
            plot = self.track_plots[key]
            ax, canvas = plot["ax"], plot["canvas"]
            ax.axis('scaled')
            ax.set_xlabel(xlabel, fontsize=font_size)
            ax.set_ylabel(ylabel, fontsize=font_size)
            ax.set_title(title, fontsize=font_size)
            canvas.draw()
                
            filename = f"{title.lower().replace(' ', '_')}.png"
            temp_elements = []

            if key == "whole_track_sideview":
                y_min, y_max = ax.get_ylim()
                padding = (y_max - y_min) * 0.8
                new_y_min = y_min - padding
                ax.set_ylim(bottom=new_y_min)

                canvas_floor_y = new_y_min                   # Absolute bottom of the image
                upper_hline_y = new_y_min + (padding * 0.85) # Upper bounding line
                lower_hline_y = new_y_min + (padding * 0.35) # Lower bounding line
                label_y = new_y_min + (padding * 0.60)       # Center of the text

                global_start_x = segment_boundaries[0]["start_x"]
                global_end_x = segment_boundaries[max(segment_boundaries.keys())]["end_x"]
                
                # Upper Horizontal Line
                upper_hline, = ax.plot([global_start_x, global_end_x], [upper_hline_y, upper_hline_y], color='red', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(upper_hline)
                # Lower Horizontal Line
                lower_hline, = ax.plot([global_start_x, global_end_x], [lower_hline_y, lower_hline_y], color='blue', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(lower_hline)

                # First Vertical Line
                first_vline, = ax.plot([global_start_x, global_start_x], [canvas_floor_y, upper_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(first_vline)
                # Last Vertical Line
                last_vline, = ax.plot([global_end_x, global_end_x], [canvas_floor_y, upper_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(last_vline)

                for idx, bounds in segment_boundaries.items():
                    start_x, end_x = bounds["start_x"], bounds["end_x"]
                    mid_x = (start_x + end_x) / 2.0
                    label_text = f"Section {idx+1}"
                    section_name = ax.text(x=mid_x, y=label_y, s=label_text, fontsize=font_size * 0.6, color='black', ha='center', va='center')
                    temp_elements.append(section_name)

                    # Subsequent vertical lines
                    if idx < len(segment_boundaries) - 1:
                        sub_vline, = ax.plot([end_x, end_x], [canvas_floor_y, lower_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=2)
                        temp_elements.append(sub_vline)

            ax.axis('off')  # Hide axis elements for a clean image
            ax.set_title(title, fontsize=font_size * 0.5)
            ax.figure.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0.1)
            ax.set_title(title, fontsize=font_size)
            ax.axis('on')   # Restore axis elements for UI display

            # Remove temp
            for element in temp_elements:
                element.remove()

            # Restore original limits if they were altered
            if key == "whole_track_sideview":
                ax.set_ylim(y_min, y_max)



    # ========================================================================
    #                       Create Helper Functions
    # ========================================================================
    def start_generating(self):
        data = []
        # Obtain track data from user inputs
        for section in self.tracks:
            for track_row in self.tracks[section]:
                track = track_row.findChild(QComboBox)
                length = track_row.findChild(QLineEdit)

                track_type = track.currentText()
                track_length = length.text()

                # Validate inputs
                if not track_type or not track_length:
                    QMessageBox.warning(self, "Incomplete Entry", "Please select a track type and enter a length for all tracks.")
                    return

                # Validate length input
                try:
                    length_value = float(track_length)
                except ValueError:
                    QMessageBox.warning(self, "Invalid Length", f"Please enter a valid number for the length of the {track_type} track.")
                    return

                # Check for valid track type and build the track segment
                if track_type not in ALL_TRACKS:
                    QMessageBox.warning(self, "Unkown Track", f"Track type {track_type} is not recognized.")
                    return

                build_func = track_function_map.get(track_type)
                if not build_func:
                        QMessageBox.warning(self, "Missing Generator", f"No building rule found for {track_type}.")
                        return
                
                segment_v_exit = 0.0
                result = build_func(length_value)

                if track_type in STARTS:
                    if isinstance(result, tuple) and len(result) == 2:
                        segment, raw_v = result
                        # Extract the float speed value if it's trapped in an array or tuple
                        if hasattr(raw_v, "__len__"):
                            segment_v_exit = float(raw_v[0])
                        else:
                            segment_v_exit = float(raw_v)
                    else:
                        segment = result
                        segment_v_exit = 0.0
                else:
                    segment = result

                # Appends to data an array list of track type and its data list
                # The data keeps tracks of section, type, and arrays for each track segment
                data.append({
                    "section": section,
                    "type": track_type,
                    "arrays": segment,
                    "v_exit": segment_v_exit
                })


        # Check if there are valid tracks to assemble
        if not data:
            QMessageBox.warning(self, "No Tracks", "No valid tracks to assemble.")
            return
        
        # Assemble and visualize tracks
        try:
            wait = QMessageBox(self)
            wait.setWindowTitle("Assembling Tracks")
            wait.setText("Assembling tracks, please wait...")
            wait.show()
            QApplication.processEvents()
            
            # print(f"DEBUG: Number of track segments being assembled: {len(data)}")
            combined_track, xy_composition, velocity_n_radius, checks = tracks.TrackPart.combine_tracks(*data)
            
            warnings = []
            for section_key, section_data in checks.items():
                if section_key == "Starts":
                    continue

                section_passed = True

                if not section_data.get("velocity_check", True):
                    warnings.append(f"• {section_key}: Not enough velocity to get through this section.")
                    section_passed = False

                if section_data.get("valley_check") is False:
                    warnings.append(f"• {section_key}: Valley G-force exceeds structural safety limits (>5G).")
                    section_passed = False

                if section_data.get("inversion_check") is False:
                    warnings.append(f"• {section_key}: Speed too low to clear inversion peak.")
                    section_passed = False

                if section_data.get("peak_check") is False:
                    warnings.append(f"• {section_key}: Speed too high over crest (Excess negative airborne Gs).")
                    section_passed = False

                if section_data.get("lateral_check") is False:
                    warnings.append(f"• {section_key}: Lateral turning G-force forces exceed safe rider comfort (>1.5G).")
                    section_passed = False

                if section_data.get("rollup_check") is False:
                    warnings.append(f"• {section_key}: Rollup incline is too tall. Train will stall.")
                    section_passed = False

                # if section_data.get("brake_check") is False:
                #     warnings.append(f"• {section_key}: Entry speed into exceeds allowed stopping threshold.")

                if section_key in self.single_page_cards:
                    card_widget = self.single_page_cards[section_key]
                    if section_passed:
                        card_widget.setStyleSheet("background-color: #2ecc71; color: #ffffff; border-radius: 10px; margin-bottom: 2px; padding: 2px;")
                    else:
                        card_widget.setStyleSheet("background-color: #e74c3c; color: #ffffff; border-radius: 10px; margin-bottom: 2px; padding: 2px;")


            wait.close()

            # Display physics failures to user if any occurred
            if warnings:
                warning_msg = "The track was built, but failed the following physics checks:\n\n" + "\n".join(warnings)
                QMessageBox.warning(self, "Physics Warning", warning_msg)

            # No matter if it fails or not, it builds the track
            self.update_visual(combined_track, xy_composition)  # Update the visualization with the combined track data and XY composition

            file_name = combined_track[-1]
            QMessageBox.information(self, "Success", f"Assembly Complete!\nCSV file generated: {file_name}")

        except Exception as e:
            if 'wait' in locals() and wait.isVisible():
                wait.close()
            QMessageBox.critical(self, "Assembly Error", f"An error occurred during assembly: {str(e)}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QLineEdit,
    QDialog, QDialogButtonBox, QSizePolicy, QStackedWidget,
    QTabWidget, QFormLayout, QSlider, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt

import tracks
from recommendation import EnergyRecommendation

# When adding new track types, they should be added to the ALL_TRACKS list and the track_function_map dictionary below.

# ========================================================================
SECTIONS = ["Starts", "Thrills 1", "Turns", "Thrills 2", "Ends"]    # Defines the sections of the track assembly
STARTS = ["Launcher", "Lift Hill", "Rollback"]                      # Defines the starting track types
THRILLS = ["Loop", "Camelback", "Corkscrew"]                        # Defines the thrill track types
TURNS = ["Cobra Roll", "Horseshoe", "Helix"]                        # Defines the turn track types
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
    "Cobra Roll": tracks.TrackPart.cobrarollCG_func,
    "Horseshoe": tracks.TrackPart.horseshoe_func,
    "Helix": tracks.TrackPart.helix_func,

    # Ends
    "Brake": tracks.TrackPart.brake_func,                   # Using this will result a return to the beginning of the track
    "Rollup": tracks.TrackPart.rollup_func                  # Has no return, but can be used to end the track with a rollup
}


# Custom Dialog Box
class StatsDialog(QDialog):
    def __init__(self, section_name, stats_data, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Statisitcs - {section_name}")
        self.resize(300, 200)
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QLabel { font-size: 12px; color: #2c3e50; }
                           """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        header_label = QLabel(f"Stats Overview for {section_name}")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2980b9;")
        main_layout.addWidget(header_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        for key, value in stats_data.items():
            key_label = QLabel(f"<b>{key}:</b>")
            val_label = QLabel(str(value))
            form_layout.addRow(key_label, val_label)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)


class DualInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Coaster Details")

        layout = QFormLayout(self)

        self.section_input = QLineEdit(self)
        self.coaster_input = QLineEdit(self)

        layout.addRow("Enter Section:", self.section_input)
        layout.addRow("Enter Coaster Name:", self.coaster_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def get_inputs(self):
        return self.section_input.text(), self.coaster_input.text()


# Custom Slider (TODO - need to fix along with recommendation.py cause that's wrong)
class RangeIndicatorSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        # Initalize with no bounds
        self.rec_min = None
        self.rec_max = None
    
    def set_recommendation_bounds(self, rec_min, rec_max):
        self.rec_min = rec_min
        self.rec_max = rec_max
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.rec_min is None or self.rec_max is None:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        slider_range = self.maximum() - self.minimum()
        if slider_range <= 0:
            return
        
        w = self.width()
        margin = 10
        usable_width = w - (2* margin)

        pos_min = margin + int(((self.rec_min - self.minimum()) / slider_range) * usable_width)
        pos_max = margin + int(((self.rec_max - self.minimum()) / slider_range) * usable_width)

        # Bound calculations to physical layout limits
        pos_min = max(margin, min(pos_min, w - margin))
        pos_max = max(margin, min(pos_max, w - margin))

        # --- Draw a transparent green background zone for the "Sweet Spot" ---
        painter.fillRect(pos_min, 4, pos_max - pos_min, self.height() - 8, QColor(46, 204, 113, 40))

        # --- Draw the Lower Target Line (Green) ---
        pen_min = QPen(QColor(39, 174, 96), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_min)
        painter.drawLine(pos_min, 2, pos_min, self.height() - 2)

        # --- Draw the Upper Target Line (Orange/Red Warning boundary) ---
        pen_max = QPen(QColor(230, 126, 34), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_max)
        painter.drawLine(pos_max, 2, pos_max, self.height() - 2)

        painter.end() 


# ===============================================================================
#                               User Interface
# ===============================================================================
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

        # Initialize stats
        self.track_stats = {}
        self.checks = {}

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
        self.visual_tab_widget.setStyleSheet("background-color: white; color: blue; font-size: 12px; font-weight: bold;")
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
            fig = Figure(figsize=(24, 12))
            canvas = FigureCanvas(fig)

            left_margin = 1.0 / 24.0
            bottom_margin = 1.0 / 12.0
            plot_width = (24.0 - 2.0) / 24.0
            plot_height = (12.0 - 2.0) / 12.0
            ax = fig.add_axes([left_margin, bottom_margin, plot_width, plot_height])

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
        scroll_area.setStyleSheet("border: none; background: transparent; color: blue; font-size: 12px; font-weight: bold;")
        
        self.single_page_widget = QWidget()
        self.single_page_widget.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; padding: 10px;")
        self.single_page_main_layout = QVBoxLayout(self.single_page_widget)
        self.single_page_main_layout.setContentsMargins(5, 5, 5, 5)
        self.single_page_main_layout.setSpacing(10)

        self.single_page_cards_layouts = {}
        self.single_page_cards = {}
        for section in SECTIONS:
            card = QWidget()
            card.setStyleSheet("background-color: #ffffff; color: blue; border-radius: 10px; margin-bottom: 2px; padding: 2px;")
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(2)

            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)
            
            title = QLabel(f"[{section}]")
            title.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 14px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stats_btn = QPushButton("[ ? ]")
            stats_btn.setStyleSheet("""
                QPushButton { background-color: #3498db;  color: white; border-radius: 5px; padding: 4px 8px; font-size: 11px; }
                QPushButton:hover { background-color: #2980b9; }
                                    """)
            
            # When the stats button is clicked, open a dialog box which shows the stats of that section
            stats_btn.clicked.connect(lambda checked, s=section: self.show_section_stats(s))
            
            header_layout.addStretch()
            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(stats_btn)
            
            # Add the horizontal header layout to the vertical card layout
            card_layout.addLayout(header_layout)

            self.single_page_cards_layouts[section] = card_layout
            self.single_page_cards[section] = card
            self.single_page_main_layout.addWidget(card)
            
        self.single_page_main_layout.addStretch()
        scroll_area.setWidget(self.single_page_widget)
        self.assembly_stack.addWidget(scroll_area)

    def tabbed_view(self):
        self.assembly_tabs = QTabWidget()
        self.assembly_tabs.setStyleSheet("""
            QTabWidget::panel {background-color: #ecf0f1; color: black; border-radius: 10px; padding: 10px; font-size: 12px; font-weight: bold;}
            QTabBar::tab {background-color: #2c3e50; color: black; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-size: 12px; font-weight: bold;}
            QTabBar::tab:selected {background-color: #ffffff; color: #2c3e50; font-size: 12px; font-weight: bold;}
        """)

        self.tab_layouts = {}
        self.tab_widgets = {}
        for section in SECTIONS:
            tab_widget = QWidget()
            tab_widget.setStyleSheet("background-color: #ffffff; color: blue; border-radius: 10px; border-top-left-radius: 0px; padding: 10px; font-size: 12px; font-weight: bold;")
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
        elif section in ("Thrills 1", "Thrills 2"):
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
        length_slider = RangeIndicatorSlider(Qt.Orientation.Horizontal)
        length_slider.setRange(1, 200)
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

        col_widget.dropdown = track_dropdown
        col_widget.input_field = length_input
        col_widget.slider = length_slider

        self.tracks[section].append(col_widget)

    def show_section_stats(self, section_name):

        if section_name in self.track_stats and section_name in self.checks:
            stats = self.track_stats[section_name]
            check_data = self.checks[section_name]

            # Determine passing status and compile active flags
            if section_name == "Starts":
                velocity_status = "PASSED"
            else:
                velocity_status = "PASSED" if check_data.get("velocity_check") else "FAILED/STALL"

            if velocity_status == "FAILED/STALL":
                section_data = {
                    "Track Status": "FAILED/STALL",
                    "Exit Velocity": "—",
                    "Apex (Top) Velocity": "—",
                    "Valley (Bottom) Velocity": "—",
                    "Apex (Top) Radius": "—",
                    "Valley (Bottom) Radius": "—",
                    "Passed Physics": "—",
                    "Failed Physics": "—"
                }
            else:
                # Format Velocities cleanly if they exist
                v_exit = f"{stats['velocity_exit']:.2f} m/s" if stats.get('velocity_exit') is not None else "N/A"
                v_top = f"{stats['v_top']:.2f} m/s" if stats.get('v_top') is not None else "N/A"
                v_bot = f"{stats['v_bottom']:.2f} m/s" if stats.get('v_bottom') is not None else "N/A"
                
                # Format Radii cleanly if they exist
                r_top = f"{stats['r_top']:.2f} m" if stats.get('r_top') is not None else "N/A"
                r_bot = f"{stats['r_bottom']:.2f} m" if stats.get('r_bottom') is not None else "N/A"
                
                
                passed_list = []
                failed_list = []
                for check_key, check_val in check_data.items():
                    if check_key == "velocity_check":
                        continue  # Handled separately by status
                    if check_val is True:
                        passed_list.append(check_key.replace("_check", "").title())
                    elif check_val is False:
                        failed_list.append(check_key.replace("_check", "").title())

                section_data = {
                    "Track Status": velocity_status,
                    "Exit Velocity": v_exit,
                    "Apex (Top) Velocity": v_top,
                    "Valley (Bottom) Velocity": v_bot,
                    "Apex (Top) Radius": r_top,
                    "Valley (Bottom) Radius": r_bot,
                    "Passed Physics": ", ".join(passed_list) if passed_list else "None",
                    "Failed Physics": ", ".join(failed_list) if failed_list else "None"
                }

        else:
            # Default is a blank state
            section_data = {
                "Track Status": "Not Generated",
                "Exit Velocity": "—",
                "Apex (Top) Velocity": "—",
                "Valley (Bottom) Velocity": "—",
                "Apex (Top) Radius": "—",
                "Valley (Bottom) Radius": "—",
                "Passed Physics": "—",
                "Failed Physics": "—"
            }
        
        # Create and display the dialog
        dialog = StatsDialog(section_name, section_data, parent=self)
        dialog.exec()

    # ========================================================================
    #                       Visual Helper Functions
    # ========================================================================
    def update_visual(self, track_data, xy_composition):
        self.placeholder_label.hide()  # Hide the placeholder label
        self.visual_tab_widget.show()  # Show the visual widget

        X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = track_data
        font_size = 8
        grid_padding = 5
        cushion = 5

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
        x_min_top, x_max_top = np.min(X), np.max(X)
        z_min_top, z_max_top = np.min(Z), np.max(Z)
        top_view_x_span = x_max_top - x_min_top
        top_view_y_span = z_max_top - z_min_top


        section_colors = {
            "sec_1": "#1f77b4",  # Blue
            "sec_2": "#ff7f0e",  # Orange
            "sec_3": "#2ca02c",  # Green
            "sec_4": "red",
            "sec_5": "blue"
        }



        # Calculate tracking properties
        total_track_length = 0
        segment_boundaries = {}
        current_horizontal_offset = 0
        
        for idx, segment in enumerate(xy_composition):
            local_horizontal = segment["XY"]
            global_2d_horizontal = local_horizontal + current_horizontal_offset
            
            segment_boundaries[idx] = {
                "start_x": global_2d_horizontal[0],
                "end_x": global_2d_horizontal[-1],
            }
            total_track_length += (local_horizontal[-1] - local_horizontal[0])
            current_horizontal_offset = global_2d_horizontal[-1]

        # Initialize the single, shared layout figure (4 rows)
        fig, axes = plt.subplots(4, 1, figsize=(24, 48))
        combined_configs = [
            {"title": "Whole Track Top View", "xlabel": "X",  "ylabel": "z", "type": "top"},
            {"title": "Section 1-2",           "xlabel": "XY", "ylabel": "Z", "type": "sec_12"},
            {"title": "Section 3",            "xlabel": "XY", "ylabel": "Z", "type": "sec_3"},
            {"title": "Section 4-5",          "xlabel": "XY", "ylabel": "Z", "type": "sec_45"}
        ]

        # --- 2. Plotting Individual Segments & Core Views ---
        # A. Plot the Native Top View to UI dict
        self.track_plots["whole_track_topview"]["ax"].plot(X, Z)

        # B. Populate Data across UI Plots and the new Combined Subplots
        current_horizontal_offset = 0
        array_idx_start = 0

        for idx, segment in enumerate(xy_composition):
            local_horizontal = segment["XY"]
            Z_elevation = segment["Z"]
            global_2d_horizontal = local_horizontal + current_horizontal_offset
            
            # Match segment color key safely
            color_key = f"sec_{idx+1}"
            segment_color = section_colors.get(color_key, "gray")

            # Update the individual standalone views
            self.track_plots["whole_track_sideview"]["ax"].plot(global_2d_horizontal, Z_elevation)

            if idx in (0, 1):
                self.track_plots["section_12"]["ax"].plot(global_2d_horizontal, Z_elevation)
            elif idx == 2:
                self.track_plots["section_3"]["ax"].plot(global_2d_horizontal, Z_elevation)
            elif idx in (3, 4):
                self.track_plots["section_45"]["ax"].plot(global_2d_horizontal, Z_elevation)


            segment_len = len(local_horizontal)
            array_idx_end = array_idx_start + segment_len
            segment_X = X[array_idx_start:array_idx_end]
            segment_Z = Z[array_idx_start:array_idx_end]
            
            axes[0].plot(segment_X, segment_Z, color=segment_color, linewidth=2)
            
            
            if idx < len(xy_composition) - 1:
                # The last index of the current segment data block
                transition_idx = array_idx_end - 1
                
                # 1. Plot dot on the standalone UI top view
                self.track_plots["whole_track_topview"]["ax"].plot(
                    X[transition_idx], Z[transition_idx], 
                    color='black', marker='o', markersize=6, zorder=5
                )
                
                # 2. Plot dot on the combined figure's top view (row 0)
                axes[0].plot(
                    X[transition_idx], Z[transition_idx], 
                    color='black', marker='o', markersize=6, zorder=5
                )

            
            
            array_idx_start = array_idx_end - 1  # Continuous connection pointer

            # Rows 1-3: Process Segment-by-Segment zero-aligned views
            for ax_idx, config in enumerate(combined_configs[1:], start=1):
                plot_type = config["type"]
                is_in_this_row = (
                    (plot_type == "sec_12" and idx in (0, 1)) or
                    (plot_type == "sec_3"  and idx == 2) or
                    (plot_type == "sec_45" and idx in (3, 4))
                )
                if is_in_this_row:
                    # Resolve row offset based on the very first element of this specific row
                    row_start_offset = segment_boundaries[0]["start_x"] if idx in (0, 1) else (
                                       segment_boundaries[2]["start_x"] if idx == 2 else 
                                       segment_boundaries[3]["start_x"])
                    
                    zero_aligned_horizontal = global_2d_horizontal - row_start_offset
                    axes[ax_idx].plot(zero_aligned_horizontal, Z_elevation, color=segment_color, linewidth=2)

            current_horizontal_offset = global_2d_horizontal[-1]

        # --- 3. Finalize Formatting, Scaling, and File Outputs ---
        # A. Format and save the individual UI plot windows
        view_configs = [
            ("whole_track_topview",     "Whole Track Top View",     "X",    "Y", True),
            ("whole_track_sideview",    "Whole Track Side View",    "XY",   "Z", False),
            ("section_12",              "Section 1-2",              "XY",   "Z", False),
            ("section_3",               "Section 3",                "XY",   "Z", False),
            ("section_45",              "Section 4-5",              "XY",   "Z", False)
        ]

        for key, title, xlabel, ylabel, is_top_view in view_configs:
            plot = self.track_plots[key]
            ax, canvas = plot["ax"], plot["canvas"]

            ax.relim()
            ax.autoscale_view()

            if is_top_view:
                ax.set_xlim(x_min_top, x_max_top)
                ax.set_ylim(z_min_top, z_max_top)
                ax.axis('scaled')
            else:
                ax.autoscale(True, axis='both')
                current_x_min, current_x_max = ax.get_xlim()
                current_y_min, current_y_max = ax.get_ylim()
                
                mid_x = (current_x_min + current_x_max) / 2.0
                mid_y = (current_y_min + current_y_max) / 2.0
                
                ax.set_xlim(mid_x - (top_view_x_span / 2.0), mid_x + (top_view_x_span / 2.0))
                ax.set_ylim(mid_y - (top_view_y_span / 2.0), mid_y + (top_view_y_span / 2.0))
                ax.axis('scaled')

            ax.set_xlabel(xlabel, fontsize=font_size)
            ax.set_ylabel(ylabel, fontsize=font_size)
            ax.set_title(title, fontsize=font_size)
            canvas.draw()
                
            filename = f"{title.lower().replace(' ', '_')}.svg"
            temp_elements = []

            # Diagram markers injection unique to individual whole sideview file
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
                
                upper_hline, = ax.plot([global_start_x, global_end_x], [upper_hline_y, upper_hline_y], color='red', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(upper_hline)
                lower_hline, = ax.plot([global_start_x, global_end_x], [lower_hline_y, lower_hline_y], color='blue', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(lower_hline)

                first_vline, = ax.plot([global_start_x, global_start_x], [canvas_floor_y, upper_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(first_vline)
                last_vline, = ax.plot([global_end_x, global_end_x], [canvas_floor_y, upper_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=1)
                temp_elements.append(last_vline)

                for idx, bounds in segment_boundaries.items():
                    mid_x_loc = (bounds["start_x"] + bounds["end_x"]) / 2.0
                    section_name = ax.text(x=mid_x_loc, y=label_y, s=f"Section {idx+1}", fontsize=font_size * 0.6, color='black', ha='center', va='center')
                    temp_elements.append(section_name)

                    if idx < len(segment_boundaries) - 1:
                        sub_vline, = ax.plot([bounds["end_x"], bounds["end_x"]], [canvas_floor_y, lower_hline_y], color='gray', linestyle='-', linewidth=0.6, zorder=2)
                        temp_elements.append(sub_vline)

            ax.axis('off')
            ax.set_title(title, fontsize=font_size * 0.5)
            ax.figure.savefig(f"Images/{filename}", dpi=300)
            ax.set_title(title, fontsize=font_size)
            ax.axis('on')

            # Clean artifacts
            for element in temp_elements:
                element.remove()
            if key == "whole_track_sideview":
                ax.set_ylim(y_min, y_max)

        # B. Format and save the multi-row combined image configuration
        for ax_idx, config in enumerate(combined_configs):
            ax = axes[ax_idx]
            plot_type = config["type"]

            if plot_type == "top":
                ax.plot(x_min_top, 0, 'go', markersize=8)
                ax.plot(x_max_top, 0, 'go', markersize=8)
                ax.set_xlim(x_min_top - cushion, x_max_top + cushion)
                ax.set_ylim(z_min_top - cushion, z_max_top + cushion)
            else:
                # Dynamically evaluate bounding constraints on drawn lines inside this specific subplot row
                lines = ax.get_lines()
                if lines:
                    local_y_all = [np.min(l.get_ydata()) for l in lines] + [np.max(l.get_ydata()) for l in lines]
                    y_base = min(local_y_all)
                else:
                    y_base = 0

                ax.set_xlim(x_min_top - cushion, x_max_top + cushion)
                ax.set_ylim(y_base - cushion, y_base + top_view_y_span + cushion)
            
            ax.set_aspect('equal', adjustable='box')
            ax.axis('off')

            single_fig = plt.figure(figsize=(24, 12))
            
            # 2. Hardcode the exact same fractional 1-inch boundaries
            s_left, s_bottom = 1.0 / 24.0, 1.0 / 12.0
            s_width, s_height = (24.0 - 2.0) / 24.0, (12.0 - 2.0) / 12.0
            single_ax = single_fig.add_axes([s_left, s_bottom, s_width, s_height])
            
            # 3. Duplicate the track lines from the current row into this single figure
            for line in ax.get_lines():
                single_ax.plot(
                    line.get_xdata(), 
                    line.get_ydata(), 
                    color=line.get_color(), 
                    linewidth=line.get_linewidth()
                )

            
            if plot_type == "top":
                dot_array_idx = 0
                for idx, segment in enumerate(xy_composition[:-1]):  # Stop before last segment
                    dot_array_idx += len(segment["XY"]) - 1
                    single_ax.plot(
                        X[dot_array_idx], Z[dot_array_idx], 
                        color='black', marker='o', markersize=6, zorder=5
                    )


            current_xlim = ax.get_xlim()
            current_ylim = ax.get_ylim()
            track_x_data = []
            track_y_data = []

            for line in ax.get_lines():
                track_x_data.extend(line.get_xdata())
                track_y_data.extend(line.get_ydata())
            track_x_data = np.array(track_x_data, dtype=float)
            track_y_data = np.array(track_y_data, dtype=float)


            if plot_type != "top":
                box_physical_width_inches = 22.0
                box_data_width = float(current_xlim[1] - current_xlim[0])
                one_inch_in_data_units = box_data_width / box_physical_width_inches
                
                step_size = 0.5 * one_inch_in_data_units  
                tooth_height = 0.5 * one_inch_in_data_units

                lowest_track_point = float(np.min(track_y_data)) if len(track_y_data) > 0 else 0.0
                y_baseline = lowest_track_point - (one_inch_in_data_units * 2.0)
                

                def get_track_height_at(x_pos):
                    if len(track_x_data) == 0:
                        return lowest_track_point
                    close_indices = np.where(np.abs(track_x_data - x_pos) <= (step_size * 2))[0]
                    if len(close_indices) > 0:
                        return float(np.min(track_y_data[close_indices]))
                    return lowest_track_point


                if len(track_x_data) > 0:
                    t_min_x, t_max_x = min(track_x_data), max(track_x_data)

                    span_width = t_max_x - t_min_x
                    num_cycles = int(span_width / (step_size * 2)) + 1

                    x_pattern = []
                    y_pattern = []
                    
                    current_x = t_min_x

                    x_pattern.append(current_x)
                    y_pattern.append(y_baseline)


                    for _ in range(num_cycles):
                        local_ceiling = get_track_height_at(current_x + (step_size / 2.0))
                        tooth_top = min(y_baseline + tooth_height, -(one_inch_in_data_units * 0.2))

                        # 1. Move DOWN (into the gap floor)
                        current_x += 0.0
                        x_pattern.extend([current_x, current_x])
                        y_pattern.extend([tooth_top, y_baseline])
                        
                        # 2. Move RIGHT (along the foundation floor gap)
                        current_x += step_size
                        x_pattern.append(current_x)
                        y_pattern.append(y_baseline)
                        
                        # 3. Move UP (forming the right wall of the gap / left wall of the next tooth)
                        current_x += 0.0
                        x_pattern.extend([current_x, current_x])
                        y_pattern.extend([y_baseline, tooth_top])
                        
                        # 4. Move RIGHT (along the top ceiling of the tooth)
                        current_x += step_size
                        x_pattern.append(current_x)
                        y_pattern.append(tooth_top)


                    single_ax.plot(
                        np.array(x_pattern, dtype=float), 
                        np.array(y_pattern, dtype=float), 
                        color='black', 
                        linewidth=1.5, 
                        linestyle='-',
                        zorder=1
                    )
                
                    single_ax.plot([t_min_x, t_min_x], [5, y_baseline], color='black', linewidth=1.5)
                    single_ax.plot([t_max_x, t_max_x], [5, y_baseline], color='black', linewidth=1.5)

                # Push the viewport limit slightly below the new 2-inch floor layout to keep it visible
                expanded_ymin = y_baseline - (one_inch_in_data_units * 0.5)
                single_ax.set_ylim(expanded_ymin, current_ylim[1])
            else:
                single_ax.set_ylim(ax.get_ylim())

        
            if len(track_x_data) > 0:
                data_min_x = np.min(track_x_data)
                data_max_x = np.max(track_x_data)
                
                # If it's a section view with foundation teeth, expand the data bounds to include them
                if plot_type != "top":
                    data_min_x = min(data_min_x, min(x_pattern))
                    data_max_x = max(data_max_x, max(x_pattern))

                # Calculate the exact center of the section data
                data_mid_x = (data_min_x + data_max_x) / 2.0
                
                # Keep the total window width uniform across all SVGs 
                total_window_width = current_xlim[1] - current_xlim[0]
                half_width = total_window_width / 2.0
                
                # Center the uniform layout window over the data midpoint
                single_ax.set_xlim(data_mid_x - half_width, data_mid_x + half_width)
            else:
                single_ax.set_xlim(ax.get_xlim())
            
            single_ax.set_aspect('equal', adjustable='box')
            single_ax.axis('off')
            
            # 5. Export as a crisp standalone file
            safe_title = config["title"].lower().replace(' ', '_').replace('-', '_')
            single_fig.savefig(
                f"Images/individual123_{safe_title}.svg",
                dpi=300,
                transparent=True,
                facecolor='none',
                pad_inches=0 # Preserves structural 1-inch borders perfectly
            )
            plt.close(single_fig) # Free up system memory instantly

        left_fraction   = 1.0 / 24.0          # Approx 0.0417
        right_fraction  = 1.0 - (1.0 / 24.0)  # Approx 0.9583
        bottom_fraction = 1.0 / 12.0          # Approx 0.0833
        top_fraction    = 1.0 - (1.0 / 12.0)  # Approx 0.9167

        total_height_span = top_fraction - bottom_fraction
        row_height = total_height_span / 4.0

        fig.subplots_adjust(
            left=left_fraction, 
            right=right_fraction, 
            bottom=bottom_fraction, 
            top=top_fraction,
        )

        fig.savefig("Images/combined_track_views.svg", dpi=300)
        plt.close(fig)





    # ========================================================================
    #               Recommendation Based on 'Starts' Input
    # ========================================================================
    # TODO (need to fix this so that the slider would give the correct thing)
    def update_recommendations(self):
        try:
            # Grab the 'Starts' section layout/widgets securely
            start_rows = self.tracks.get("Starts", [])
            if not start_rows:
                return
                
            # Get the first row in the Starts section
            start_row = start_rows[0] 
            
            # Securely find the drop-down and text input using findChild
            start_dropdown = start_row.findChild(QComboBox)
            start_input = start_row.findChild(QLineEdit)
            
            # If the UI hasn't fully rendered these yet, exit safely without crashing
            if not start_dropdown or not start_input:
                return
                
            # Extract current type and value
            start_type = start_dropdown.currentText()
            try:
                start_val = float(start_input.text())
            except ValueError:
                return # User is still typing, or it's empty
                
            # Get recommendations based on total initial energy
            recs = EnergyRecommendation.get_recommendations(start_type, start_val)
            
            # Loop through all subsequent sections to update their slider bounds
            for section_key in ["Thrills 1", "Turns", "Thrills 2"]:
                for row in self.tracks.get(section_key, []):
                    row_dropdown = row.findChild(QComboBox)
                    row_slider = row.findChild(RangeIndicatorSlider)
                    
                    # Skip if this specific row row isn't fully drawn yet
                    if not row_dropdown or not row_slider:
                        continue
                        
                    track_type = row_dropdown.currentText()
                    
                    if track_type in recs:
                        min_rec, max_rec = recs[track_type]
                        row_slider.set_recommendation_bounds(min_rec, max_rec)
                                
                            
        except Exception as e:
            print(f"Recommendation update idle: {e}")


    # ========================================================================
    #                           Proccesing Data
    # ========================================================================
    def process_data(self):
        return


    # ========================================================================
    #                       Proccesing Physics Checks
    # ========================================================================
    def process_physics_checks(self, checks):
        warnings = []
        for section_key, section_data in checks.items():
            if section_key == "Starts":
                continue

            section_passed = True

            if not section_data.get("velocity_check", True):
                warnings.append(f"{section_key}: Not enough velocity to get through this section.")
                section_passed = False

            if section_data.get("valley_check") is False:
                warnings.append(f"{section_key}: Valley G-force exceeds 5Gs.")
                section_passed = False

            if section_data.get("inversion_check") is False:
                warnings.append(f"{section_key}: Not enough speed to clear inversion peak.")
                section_passed = False

            if section_data.get("peak_check") is False:
                warnings.append(f"{section_key}: Speed too high over crest (Airborne).")
                section_passed = False

            if section_data.get("lateral_check") is False:
                warnings.append(f"{section_key}: Lateral turning G-forces exceed safe rider comfort (>1.5G).")
                section_passed = False

            if section_data.get("rollup_check") is False:
                warnings.append(f"{section_key}: Rollup incline is too tall. Train will stall.")
                section_passed = False

            if section_data.get("brake_check") is False:
                warnings.append(f"{section_key}: Entry speed into exceeds allowed stopping threshold.")
                section_passed = False

            # Changes the color of the section, based on whether they passed or failed the checks
            if section_key in self.single_page_cards:
                card_widget = self.single_page_cards[section_key]
                if section_passed:
                    card_widget.setStyleSheet("background-color: #2ecc71; color: #ffffff; border-radius: 10px; margin-bottom: 2px; padding: 2px;")
                else:
                    card_widget.setStyleSheet("background-color: #e74c3c; color: #ffffff; border-radius: 10px; margin-bottom: 2px; padding: 2px;")

        return warnings


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
        
        # === Ask the user for their section and coaster name ===
        dialog = DualInputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            section_name, coaster_name = dialog.get_inputs()

            if not section_name.strip():
                section_name = "Test"
            if not coaster_name.strip():
                coaster_name = "Combined Coaster"
            print(f"Section: {section_name} | Coaster: {coaster_name}")
        
        else:
            return

        wait = QMessageBox(self)
        wait.setWindowTitle("Assembling Tracks")
        wait.setText("Assembling tracks, please wait...")
        wait.show()
        QApplication.processEvents()

        # Assemble and visualize tracks
        try:
            combined_track, xy_composition, track_stats, checks = tracks.TrackPart.combine_tracks(*data, coaster_name=coaster_name)
            self.track_stats, self.checks = track_stats, checks

            if wait.isVisible():  
                wait.close()

            # Display physics failures to user if any occurred
            warnings = self.process_physics_checks(checks)
            if warnings:
                warning_msg = "The track was built, but failed the following physics checks:\n\n" + "\n".join(warnings)
                QMessageBox.warning(self, "Physics Warning", warning_msg)

            self.update_recommendations()                       # Update slider recommendation
            self.update_visual(combined_track, xy_composition)  # Update the visualization panel

            QMessageBox.information(self, "Success", f"Assembly Complete!\nCSV file generated: {coaster_name}")

        except Exception as e:
            if 'wait' in locals() and wait.isVisible():
                wait.close()
            QMessageBox.critical(self, "Assembly Error", f"An error occurred during assembly: {str(e)}")


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as sys_error:
        print(f"CRITICAL SYSTEM CRASH DETECTED: {sys_error}")

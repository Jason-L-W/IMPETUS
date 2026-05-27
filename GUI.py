import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QLineEdit,
    QSpacerItem, QSizePolicy, QStackedWidget,
    QTabWidget, QFormLayout, QSlider, QScrollArea
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import tracks
import build

SECTIONS = ["Starts", "Thrills 1", "Turns", "Thrills 2", "Ends"]
STARTS = ["Launch", "Lift Hill[x]", "Rollback[x]"]
THRILLS = ["Loop", "Camelback", "Corkscrew"]
TURNS = ["Cobral Roll", "Horseshoe[x]", "Helix[x]"]
ENDS = ["Brake", "Rollup[x]"]
ALL_TRACKS = STARTS + THRILLS + TURNS + ENDS

track_function_map = {
    # Starts
    "Launch": tracks.TrackPart.brake_func,
    "Lift Hill[x]": tracks.TrackPart.lifthill_func,
    "Rollback[x]": tracks.TrackPart.rollback_func,

    # Thrills
    "Loop": tracks.TrackPart.loopCG_func,
    "Camelback": tracks.TrackPart.camelback_func,
    "Corkscrew": tracks.TrackPart.corkscrew_func,

    # Turns
    "Cobral Roll": tracks.TrackPart.cobrarollCG_func,
    "Horseshoe[x]": tracks.TrackPart.horseshoe_func,
    "Helix[x]": tracks.TrackPart.helix_func,

    # Ends
    "Brake": tracks.TrackPart.brake_func,
    "Rollup[x]": tracks.TrackPart.rollup_func

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

        self.assembly_panel()
        self.visual_panel()
        self.layout.addWidget(self.track_widget)
        self.create_button()

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

        selector_layout = QHBoxLayout()
        selector_label = QLabel("View Mode: ")
        selector_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

        self.setup_selector = QComboBox()
        self.setup_selector.addItems(["Setup 1: All on 1 Page", "Setup 2: Tabbed View"])
        self.setup_selector.setStyleSheet("""
            QComboBox { background-color: white; color: #2c3e50; padding: 6px; border-radius: 5px; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: white; border-radius: 5px; }
                                          """)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.setup_selector)
        self.assembly_layout.addLayout(selector_layout)

        self.assembly_stack = QStackedWidget()
        self.assembly_layout.addWidget(self.assembly_stack)

        self.single_page_view() # Setup 1: All on 1 page
        self.tabbed_view()      # Setup 2: Multiple pages

        self.setup_selector.currentIndexChanged.connect(self.switch_view_mode)
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
        self.visual_tab_widget.setStyleSheet("background-color: white; color: black;")
        self.visual_tab_widget.hide()
        self.visual_constent_layout.addWidget(self.visual_tab_widget)

        # Tab 1: 3D Visualization
        self.figure_3d = Figure()
        self.canvas = FigureCanvas(self.figure_3d)
        self.ax3d = self.figure_3d.add_subplot(111, projection='3d')
        self.visual_tab_widget.addTab(self.canvas, "3D View")

        # Tab 2: 2D Visualization (X-Axis)
        self.figure_2d_x = Figure()
        self.canvas_2d_x = FigureCanvas(self.figure_2d_x)
        self.ax_x = self.figure_2d_x.add_subplot(111)
        self.visual_tab_widget.addTab(self.canvas_2d_x, "2D View (XY)")

        # Tab 3: 2D Visualization (Y-Axis)
        self.figure_2d_y = Figure()
        self.canvas_2d_y = FigureCanvas(self.figure_2d_y)
        self.ax_y = self.figure_2d_y.add_subplot(111)
        self.visual_tab_widget.addTab(self.canvas_2d_y, "2D View (XZ)")

        # Tab 4: 2D Visualization (Z-Axis)
        self.figure_2d_z = Figure()
        self.canvas_2d_z = FigureCanvas(self.figure_2d_z)
        self.ax_z = self.figure_2d_z.add_subplot(111)
        self.visual_tab_widget.addTab(self.canvas_2d_z, "2D View (YZ)")

        self.track_layout.addWidget(self.visual_widget, 1)


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
        scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.single_page_widget = QWidget()
        self.single_page_widget.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; padding: 10px;")
        self.single_page_main_layout = QVBoxLayout(self.single_page_widget)
        self.single_page_main_layout.setContentsMargins(5, 5, 5, 5)
        self.single_page_main_layout.setSpacing(10)

        self.single_page_card_layouts = {}
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
            
            self.single_page_card_layouts[section] = card_layout
            self.single_page_main_layout.addWidget(card)
            
        self.single_page_main_layout.addStretch()
        scroll_area.setWidget(self.single_page_widget)
        self.assembly_stack.addWidget(scroll_area)

    def tabbed_view(self):
        self.assembly_tabs = QTabWidget()
        self.assembly_tabs.setStyleSheet("""
            QTabWidget::panel {background-color: #ecf0f1; border-radius: 10px; padding: 10px;}
            QTabBar::tab {background-color: #2c3e50; color: white; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px;}
            QTabBar::tab:selected {background-color: #ffffff; color: #2c3e50; font-weight: bold;}
        """)

        self.tab_layouts = {}
        for section in SECTIONS:
            tab_widget = QWidget()
            tab_widget.setStyleSheet("background-color: #ffffff; border-radius: 10px; border-top-left-radius: 0px; padding: 10px;")
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(5, 5, 5, 5)
            
            self.tab_layouts[section] = tab_layout
            self.assembly_tabs.addTab(tab_widget, section)
            
        self.assembly_stack.addWidget(self.assembly_tabs)

    def switch_view_mode(self, index):
        # The default is all on 1 page, but can change between them if the user wants

        for section in SECTIONS:
            if index == 0:
                target_layout = self.single_page_card_layouts[section]
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

        # Setup the Slider
        length_slider = QSlider(Qt.Orientation.Horizontal)
        length_slider.setRange(1, 100)
        
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
    def update_visual(self, track_data):
        self.placeholder_label.hide()  # Hide the placeholder label
        self.visual_tab_widget.show()  # Show the visual widget

        X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = track_data

        # 3D View
        self.ax3d.clear()
        self.ax3d.plot3D(X, Y, Z, 'b-', label='Track Path')
        self.ax3d.scatter(X + Nx, Y + Ny, Z + Nz, color='r', label='Normals')
        self.ax3d.set_xlabel("X")
        self.ax3d.set_ylabel("Y")
        self.ax3d.set_zlabel("Z")
        self.ax3d.set_title(f"3D Track Visualization: {file_name}")
        self.ax3d.legend()
        self.canvas.draw()

        # 2D View (XY View)
        self.ax_x.clear()
        self.ax_x.plot(X, Y, 'g-')
        self.ax_x.set_xlabel("X")
        self.ax_x.set_ylabel("Y")
        self.ax_x.set_title("2D Track Visualization (XY View)")
        self.ax_x.legend()
        self.canvas_2d_x.draw()

        # 2D View (XZ View)
        self.ax_y.clear()
        self.ax_y.plot(X, Z, 'o-')
        self.ax_y.set_xlabel("X")
        self.ax_y.set_ylabel("Z")
        self.ax_y.set_title("2D Track Visualization (XZ View)")
        self.ax_y.legend()
        self.canvas_2d_y.draw()

        # 2D View (YZ View)
        self.ax_z.clear()
        self.ax_z.plot(Y, Z, 's-')
        self.ax_z.set_xlabel("Y")
        self.ax_z.set_ylabel("Z")
        self.ax_z.set_title("2D Track Visualization (YZ View)")
        self.ax_z.legend()
        self.canvas_2d_z.draw()


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
                if track_type in ALL_TRACKS:
                    build_func = track_function_map.get(track_type)
                    if build_func:
                        segment = build_func(length_value)
                        # Appends an array list of track type and its data list
                        data.append({
                            "type": track_type,
                            "is_end": track_type in ENDS,
                            "arrays": segment
                        })
                    else:
                        QMessageBox.warning(self, "Unknown Track", f"Track type {track_type} is not recognized.")
                        return

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
            
            combined_track = tracks.TrackPart.combine_tracks(*data)
            self.update_visual(combined_track)

            # Used later to display total length, total height, etc.
            X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = combined_track

            wait.setText(f"Assembly Complete!\nCSV file generated: {file_name}")
            wait.close()

        except Exception as e:
            QMessageBox.critical(self, "Assembly Error", f"An error occurred during assembly: {str(e)}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    test = 1
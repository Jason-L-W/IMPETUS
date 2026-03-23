import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QLineEdit,
    QSpacerItem, QSizePolicy, QScrollArea, QStackedWidget
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import tracks
import build
from time import sleep

# Magic numbers for track types and sections, can adjust later to be more specific with track types and options
SECTIONS = ["Starts", "Thrills", "Turns", "Ends"]
STARTS = ["Launch", "Lift Hill[x]", "Rollback[x]"]
THRILLS = ["Loop", "Camelback", "Corkscrew"]
TURNS = ["Cobral Roll", "Horseshoe[x]", "Helix[x]"]
ENDS = ["Brake", "Rollup[x]"]
ALL_TRACKS = STARTS + THRILLS + TURNS + ENDS
INITAL_TRACKS = 1

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
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Title
        title = QLabel("IMPETUS RollerCoaster Track Builder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 10px; background-color: #34495e; border-radius: 10px;")
        title.setFixedHeight(60)
        self.layout.addWidget(title)

        # Spacer Item
        self.assembly_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Track Panel (Assembly and Visualization)
        self.track_widget = QWidget()
        self.track_widget.setStyleSheet("background-color: green; border-radius: 10px; padding: 10px;")
        self.track_layout = QHBoxLayout(self.track_widget)

        # Assembly and Visualization Panels
        self.assembly_panel()
        self.visualization_panel()
        self.layout.addWidget(self.track_widget)
        # Add Start Assembly Button
        self.start_assembly_button()

    # Assembly/Visualization Panels and Button
    # ================================================================================================================
    # Assembly Panel
    def assembly_panel(self):
        # Assembly Panel
        self.assembly_widget = QWidget()
        self.assembly_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; padding: 10px;")
        self.assembly_layout = QVBoxLayout(self.assembly_widget)

        # Assembly Label
        track_assembly_label = QLabel("Track Assembly")
        track_assembly_label.setStyleSheet(
            "color: blue; font-size: 20px; background-color: white;"
            "padding: 5px; border-radius: 5px;"
        )
        track_assembly_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        track_assembly_label.setFixedHeight(40)
        self.assembly_layout.addWidget(track_assembly_label)
        self.assembly_layout.addItem(self.assembly_spacer)

        # Track Assembly Panel (would include 4 sections: starts, thrills, turns, ends)
        self.track_assembly_widget = QWidget()
        self.track_assembly_widget.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; padding: 10px;")
        self.assembly_layout.addWidget(self.track_assembly_widget)
        self.track_assembly_layout = QVBoxLayout(self.track_assembly_widget)

        # Tracks dictionary to keep track of tracks added in each section, can adjust later to be more specific with track types and options
        self.section_layouts = {}
        self.tracks = {section: [] for section in SECTIONS}

        for section in SECTIONS:
            section_container = QWidget()
            section_container.setStyleSheet("background-color: #bdc3c7; border-radius: 10px; padding: 10px;")
            
            container_layout = QVBoxLayout(section_container)

            # Header Row with Section Label and Add/Remove Buttons
            header_layout = QHBoxLayout()
            label = QLabel(section)
            label.setStyleSheet(
                "color: #2c3e50; font-size: 18px; background-color: #bdc3c7;"
                "padding: 5px; border-radius: 5px;"
            )
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            # Add Track Button (add to the end of the section)
            add_track_button = QPushButton("+")
            add_track_button.setStyleSheet(
                "background-color: #3498db; color: white; font-size: 16px;"
                "font-weight: bold; padding: 5px 8px; border-radius: 5px;"
            )
            add_track_button.clicked.connect(lambda checked, s=section: self.create_track_row(s))

            # Remove Track Button (remove from the end of the section)
            remove_track_button = QPushButton("-")
            remove_track_button.setStyleSheet(
                "background-color: #e74c3c; color: white; font-size: 16px;"
                "font-weight: bold; padding: 5px 8px; border-radius: 5px;"
            )
            remove_track_button.clicked.connect(lambda checked, s=section: self.remove_track_row(s))
            
            # Add widgets to header layout
            header_layout.addWidget(label)
            header_layout.addStretch()
            header_layout.addWidget(add_track_button)
            header_layout.addWidget(remove_track_button)

            container_layout.addLayout(header_layout)

            # Layout for track rows in each section
            rows_layout = QVBoxLayout()
            container_layout.addLayout(rows_layout)

            self.section_layouts[section] = rows_layout
            self.track_assembly_layout.addWidget(section_container)

            # Certain track types can have no more than 1 track in a section
            for _ in range(INITAL_TRACKS):
                if section == "Turns" and len(self.tracks[section]) >= 1:
                    break
                self.create_track_row(section)

        # Add Assembly Panel to Main Layout
        self.track_layout.addWidget(self.assembly_widget)

    # Visualization Panel
    def visualization_panel(self):
        # Visual Panel
        self.visual_widget = QWidget()
        self.visual_widget.setStyleSheet("background-color: #bdc3c7; border-radius: 10px; padding: 10px;")
        visual_layout = QVBoxLayout(self.visual_widget)

        # Visualization Label
        visual_label = QLabel("Track Visualization")
        visual_label.setStyleSheet(
            "color: blue; font-size: 20px; background-color: white;"
            "padding: 5px; border-radius: 5px;"
        )
        visual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        visual_label.setFixedHeight(40)
        visual_layout.addWidget(visual_label)
        self.assembly_layout.addItem(self.assembly_spacer)

        self.view_stack = QStackedWidget()
        visual_layout.addWidget(self.view_stack)

        # Placeholder Label
        self.placeholder_label = QLabel("Track visualization will appear here after assembly.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #7f8c8d; font-size: 16px;")
        self.placeholder_label.setWordWrap(True)
        self.view_stack.addWidget(self.placeholder_label)

        # Matplotlib Figure and Canvas for Visualization
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax3d = self.figure.add_subplot(111, projection='3d')

        self.view_stack.addWidget(self.canvas)
        self.track_layout.addWidget(self.visual_widget)

    # Start Assembly Button
    def start_assembly_button(self):
        self.start_button = QPushButton("Start Assembly")
        self.start_button.setStyleSheet(
            "background-color: #2ecc71; color: white; font-size: 18px;"
            "padding: 10px; border-radius: 10px;"
        )
        self.start_button.clicked.connect(self.start_assembly)
        self.layout.addWidget(self.start_button)

    # Functions
    # ================================================================================================================
    # Resize Event to adjust panel sizes
    def resizeEvent(self, event):
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        self.assembly_widget.setMaximumWidth(min(self.width() // 2 - 40, screen_width // 2))
        self.assembly_widget.setMaximumHeight(min(self.height() - 150, screen_height - 150))

        self.visual_widget.setMaximumWidth(min(self.width() // 2 - 40, screen_width // 2))
        self.visual_widget.setMaximumHeight(min(self.height() - 150, screen_height - 150))

        self.setMaximumWidth(screen_width)
        self.setMaximumHeight(screen_height)

        super().resizeEvent(event)

    # Create a new track row in the specified section with track type dropdown and length input, can adjust later to include more options for certain track types
    def create_track_row(self, section):
        # Validate section
        if section not in self.tracks:
            QMessageBox.warning(self, "Invalid Section", "The specified section does not exist.")
            return
        
        # Limit the number of tracks in the Turns section to 1
        if section == "Turns" and len(self.tracks[section]) >= 1:
            QMessageBox.warning(self, "Limit Reached", "Only one track can be added to the Turns section.")
            return
        
        # Keeps track of number of tracks added and set a maximum amount of tracks
        if len(self.tracks[section]) >= 3:
            QMessageBox.warning(self, "Limit Reached", "Maximum number of tracks has been reached for this section.")
            return
        
        # Create a new track row
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)

        track_dropdown = QComboBox()
        track_dropdown.setPlaceholderText("Select Track Type")

        if section == "Starts":
            track_dropdown.addItems(STARTS)
        elif section == "Thrills":
            track_dropdown.addItems(THRILLS)
        elif section == "Turns":
            track_dropdown.addItems(TURNS)
        elif section == "Ends":
            track_dropdown.addItems(ENDS)
        
        length_input = QLineEdit()
        length_input.setPlaceholderText("Track Length")

        row_layout.addWidget(track_dropdown)
        row_layout.addWidget(length_input)

        target_layout = self.section_layouts[section]
        target_layout.addWidget(row_widget)
        self.tracks[section].append(row_widget)

        # Connect change event to update options (Some tracks may need more options)
        # track_dropdown.currentIndexChanged.connect(self.update_track_options)

    # Remove the last track row added (can adjust later to remove specific tracks)
    def remove_track_row(self, section):
        if len(self.tracks[section]) == 1:
            QMessageBox.warning(self, "Minimum Tracks", "At least one track must be present in this section.")
            return
        
        section_tracks = self.tracks.get(section, [])

        if section_tracks:
            row_widget = section_tracks.pop()
            row_widget.deleteLater()

    # Update track options based on selected track type
    # Some tracks may need additional parameters (1 or 2)
    def update_track_options(self):
        selected = self.track.currentText()
        if selected == "Loop de Loop":
            g_force = QLineEdit()
            g_force.setPlaceholderText("G-Force (default 4g)")
            index = self.track_assembly_layout.indexOf(self.assembly_spacer)
            self.track_assembly_layout.insertWidget(index, g_force)
        elif selected == "Loop 2 R":
            radius1 = QLineEdit()
            radius1.setPlaceholderText("Radius")
            index = self.track_assembly_layout.indexOf(self.assembly_spacer)
            self.track_assembly_layout.insertWidget(index, radius1)
        else:
            # length = QLineEdit()
            # length.setPlaceholderText("Track Length")
            # index = self.track_assembly_layout.indexOf(self.assembly_spacer)
            # self.track_assembly_layout.insertWidget(index, length)
            pass


    # Assembly
    # ================================================================================================================
    # Start Assembly Button Action
    def start_assembly(self):
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
            # build.plot(combined_track) # For now it is seperate, but will integrate into UI later
            self.update_visualization(combined_track)

            # Used later to display total length, total height, etc.
            X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = combined_track

            wait.setText(f"Assembly Complete!\nCSV file generated: {file_name}")
            wait.close()

        except Exception as e:
            QMessageBox.critical(self, "Assembly Error", f"An error occurred during assembly: {str(e)}")

    # Visualization
    def update_visualization(self, track_data):
        self.view_stack.setCurrentIndex(1)  # Switch to the visualization view

        X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = track_data

        self.ax3d.clear()
        self.ax3d.plot3D(X, Y, Z, 'b-', label='Track Path')
        self.ax3d.scatter(X + Nx, Y + Ny, Z + Nz, color='r', label='Normals')

        self.ax3d.set_xlabel("X")
        self.ax3d.set_ylabel("Y")
        self.ax3d.set_zlabel("Z")
        self.ax3d.set_title(f"Track Visualization: {file_name}")
        self.ax3d.legend()

        self.canvas.draw()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
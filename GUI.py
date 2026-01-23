import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QLineEdit,
    QSpacerItem, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt


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
        title.setStyleSheet(
            "color: white; font-size: 24px; font-weight: bold;"
            "padding: 10px; background-color: #34495e; border-radius: 10px;"
        )
        title.setFixedHeight(60)
        self.layout.addWidget(title)

        # Spacer Item
        self.assembly_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # ================================================================================================================
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

        # Track Assembly Panel
        self.track_assembly_widget = QWidget()
        self.track_assembly_widget.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; padding: 10px;")
        self.assembly_layout.addWidget(self.track_assembly_widget)
        self.track_assembly_layout = QVBoxLayout(self.track_assembly_widget)

        # Tracks List
        self.tracks = []

        # Initial Tracks
        for _ in range(3):
            self.create_track_row()

        # Add Track Button
        self.add_track_button = QPushButton("Add Track")
        self.add_track_button.setStyleSheet(
            "background-color: #3498db; color: white; font-size: 16px;"
            "padding: 8px; border-radius: 5px;"
        )
        self.add_track_button.clicked.connect(self.create_track_row)
        self.assembly_layout.addWidget(self.add_track_button)

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

        # Placeholder for 3D Visualization
        placeholder_label = QLabel("3D Visualization Placeholder")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(
            "color: black; font-size: 16px;"
            "background-color: #95a5a6; padding: 50px; border-radius: 10px;"
        )
        visual_layout.addWidget(placeholder_label)

        # Add Visual Panel to Main Layout
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

    # Create a new track row in the assembly panel
    def create_track_row(self):
        # Keeps track of number of tracks added and set a maximum amount of tracks
        track_counter = len(self.tracks) + 1
        if track_counter > 10:
            QMessageBox.warning(self, "Limit Reached", "Maximum number of tracks has been reached.")
            return

        row = QHBoxLayout(self.track_assembly_widget)

        track = QComboBox()
        track.setPlaceholderText("Select Track Type")
        track.addItems(["Camelback", "Cobral Roll", "Corkscrew"])

        length = QLineEdit()
        length.setPlaceholderText("Track Length")

        row.addWidget(track)
        row.addWidget(length)
        row.addStretch()

        index = self.track_assembly_layout.indexOf(self.assembly_spacer)
        self.track_assembly_layout.insertLayout(index, row)
        self.tracks.append((track, length))

    # Start Assembly Button Action
    def start_assembly(self):
        data = []
        for track, length in self.tracks:
            if track.currentText() == "" or length.text() == "":
                QMessageBox.warning(
                    self,
                    "Incomplete Entry",
                    "Please select a track type and enter a length for all tracks."
                )
                return
            else:
                data.append(f"{track.currentText()} - Length: {length.text()}")
            
        print(data)  # For debugging purposes

        QMessageBox.information(
            self,
            "Track Assembly",
            "Tracks:\n" + ("\n".join(data) if data else "No tracks defined.")
        )

    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
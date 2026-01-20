import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QSizePolicy, QLineEdit
from PyQt6.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track RollerCoaster")
        self.setGeometry(100, 100, 600, 400)

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.main_widget)
        
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Title Label
        self.title = QLabel("IMPETUS RollerCoaster Track Builder")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 10px; background-color: #34495e; border-radius: 10px;")
        self.layout.addWidget(self.title)


        # Panels
        # ------------------------------------------------------------------------------------------------------#
        # Track Panel (Includes Assembly and Visual Panels)
        track_panel = QWidget()
        track_panel.setStyleSheet("background-color: green; border-radius: 10px; padding: 15px;")
        track_layout = QHBoxLayout()
        track_panel.setLayout(track_layout)

        # Assembly Panel
        assembly_panel = QWidget()
        assembly_panel.setStyleSheet("background-color: blue; border-radius: 10px; padding: 15px;")
        assembly_layout = QVBoxLayout()
        assembly_panel.setLayout(assembly_layout)
        track_layout.addWidget(assembly_panel)

        # Visual Panel
        visual_panel = QWidget()
        visual_panel.setStyleSheet("background-color: #bdc3c7; border-radius: 10px; padding: 15px;")
        visual_layout = QVBoxLayout()
        visual_panel.setLayout(visual_layout)
        track_layout.addWidget(visual_panel)

        self.layout.addWidget(track_panel)
        # ------------------------------------------------------------------------------------------------------#
    

        # Track Assembly Components
        # ------------------------------------------------------------------------------------------------------#
        track_label = QLabel("Track Assembly")
        track_label.setStyleSheet("color: blue; font-size: 20px; background-color: white; padding: 5px; border-radius: 5px;")
        assembly_layout.addWidget(track_label)

        track_combo_1 = QComboBox()
        track_combo_1.addItems(["Track 1", "Track 2", "Track 3"])
        assembly_layout.addWidget(track_combo_1)
        track_length1 = QLineEdit()
        track_length1.setPlaceholderText("Enter Track Length")
        assembly_layout.addWidget(track_length1)
        
        self.track_combo2 = QComboBox()
        self.track_combo2.addItems(["Track 1", "Track 2", "Track 3"])
        assembly_layout.addWidget(self.track_combo2)
        self.track_length2 = QLineEdit()
        self.track_length2.setPlaceholderText("Enter Track Length")
        assembly_layout.addWidget(self.track_length2)

        self.track_combo3 = QComboBox()
        self.track_combo3.addItems(["Track 1", "Track 2", "Track 3"])
        assembly_layout.addWidget(self.track_combo3)
        self.track_length3 = QLineEdit()
        self.track_length3.setPlaceholderText("Enter Track Length")
        assembly_layout.addWidget(self.track_length3)

        def add_track():
            new_track_combo = QComboBox()
            new_track_combo.addItems(["Track 1", "Track 2", "Track 3"])
            assembly_layout.addWidget(new_track_combo)
            new_track_length = QLineEdit()
            new_track_length.setPlaceholderText("Enter Track Length")
            assembly_layout.addWidget(new_track_length)

        add_track_button = QPushButton("Add Track")
        add_track_button.setStyleSheet("background-color: #3498db; color: white; font-size: 14px; padding: 5px; border-radius: 5px;")
        add_track_button.clicked.connect(add_track)
        assembly_layout.addWidget(add_track_button)

        self.layout.addWidget(track_panel)
        # ------------------------------------------------------------------------------------------------------#


        # Track Visualization Components (This will be a placeholder for now, uses matplotlib later)
        # ------------------------------------------------------------------------------------------------------#
        visual_label = QLabel("Track Visualization")
        visual_label.setStyleSheet("color: blue; font-size: 20px; background-color: white; padding: 5px; border-radius: 5px;")
        visual_layout.addWidget(visual_label)
        # Placeholder for 3D Visualization
        placeholder_label = QLabel("3D Visualization Placeholder")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: black; font-size: 16px; background-color: #95a5a6; padding: 50px; border-radius: 10px;")
        visual_layout.addWidget(placeholder_label)
        self.layout.addWidget(track_panel)
        # ------------------------------------------------------------------------------------------------------#


        # Build Track Button (Need to connect functionality later)
        # ------------------------------------------------------------------------------------------------------#
        self.start_button = QPushButton("Start Assembly")
        self.start_button.setStyleSheet("background-color: #2ecc71; color: white; font-size: 18px; padding: 10px; border-radius: 10px;")
        self.start_button.clicked.connect(self.start_assembly)
        self.layout.addWidget(self.start_button)
        # ------------------------------------------------------------------------------------------------------#



    def start_assembly(self):
        selected_track = self.track_combo.currentText()
        QMessageBox.information(self, "Track Selected", f"You have selected: {selected_track}")






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
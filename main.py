import sys
import os
import shutil # <-- Import shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
                             QCheckBox, QFileDialog, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QIcon
from PIL import Image, ImageQt

class DensityGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.input_image_path = None
        # Calculate default output directory relative to the script file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.default_output_dir = os.path.join(script_dir, "generated_drawables")
        self.output_dir = self.default_output_dir # Default to this path initially
        self.initUI()
        
        # Set window icon (try both icon.svg and icon.png as fallback)
        self.setWindowIcon(self.load_app_icon())

    def load_app_icon(self):
        """Load the application icon from either icon.svg or icon.png file"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path_svg = os.path.join(script_dir, "icon.svg")
        icon_path_png = os.path.join(script_dir, "icon.png")
        
        # Create an icon instance
        icon = QIcon()
        
        # Try to load SVG first (preferred)
        if os.path.exists(icon_path_svg):
            icon.addFile(icon_path_svg)
        # Fall back to PNG if SVG not found or didn't load properly
        elif os.path.exists(icon_path_png):
            icon.addFile(icon_path_png)
            
        return icon

    def initUI(self):
        self.setWindowTitle('Android Density Image Generator (Input: xxxhdpi)')
        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        # Drag and Drop Area
        self.drop_label = QLabel("Drag & Drop XXXHDPI Image Here")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")
        self.drop_label.setMinimumHeight(100)
        self.drop_label.setAcceptDrops(True)
        self.drop_label.dragEnterEvent = self.dragEnterEvent
        self.drop_label.dropEvent = self.dropEvent
        layout.addWidget(self.drop_label)

        # Density Selection - Now includes xxxhdpi and defaults to checked
        self.density_checkboxes = {}
        density_layout = QHBoxLayout()
        # Include all densities including the base xxxhdpi for output structure
        densities = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
        for density in densities:
            checkbox = QCheckBox(density)
            checkbox.setChecked(True) # <-- Default to checked
            self.density_checkboxes[density] = checkbox
            density_layout.addWidget(checkbox)
        layout.addLayout(density_layout)

        # Output Directory Selection - Shows default path initially
        output_layout = QHBoxLayout()
        self.select_output_btn = QPushButton("Select Output Directory")
        self.select_output_btn.clicked.connect(self.select_output_dir)
        # Display the default directory initially
        self.output_dir_label = QLabel(f"Output: {self.output_dir}")
        self.output_dir_label.setWordWrap(True)
        output_layout.addWidget(self.select_output_btn)
        output_layout.addWidget(self.output_dir_label)
        layout.addLayout(output_layout)

        # Generate Button
        self.generate_btn = QPushButton("Generate Images")
        self.generate_btn.clicked.connect(self.generate_images)
        layout.addWidget(self.generate_btn)

        self.setLayout(layout)
        self.resize(450, 350) # Slightly wider for more checkboxes

    # --- Drag and Drop Handlers ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        # Accept drops if they contain URLs (which includes local file paths)
        if event.mimeData().hasUrls():
            # Check if it's a single file and likely an image
            urls = event.mimeData().urls()
            if len(urls) == 1:
                 url = urls[0]
                 if url.isLocalFile():
                     file_path = url.toLocalFile()
                     # Basic check for common image extensions
                     if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                        event.acceptProposedAction()
                        self.drop_label.setStyleSheet("border: 2px dashed #0078d7; background-color: #e0f0ff; padding: 20px;") # Highlight
                        return
        event.ignore()
        self.drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;") # Reset style if ignored

    def dragLeaveEvent(self, event):
        self.drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;") # Reset style

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            url = urls[0]
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    self.input_image_path = file_path
                    # Attempt to display thumbnail
                    try:
                        pixmap = QPixmap(file_path)
                        if not pixmap.isNull():
                             # Scale pixmap more reliably
                             label_size = self.drop_label.size()
                             scaled_pixmap = pixmap.scaled(label_size * 0.9, # Use slightly less than full label size
                                                            Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation)
                             self.drop_label.setPixmap(scaled_pixmap)
                             self.drop_label.setText("")
                        else:
                             self.drop_label.setText(f"""Loaded: {os.path.basename(file_path)}
(Preview failed)""")
                    except Exception as e:
                         print(f"Error loading preview: {e}")
                         self.drop_label.setText(f"Loaded: {os.path.basename(file_path)}")

                    self.drop_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
                    event.acceptProposedAction()
                    return
        event.ignore()
        self.drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")

    # --- Button Click Handlers ---
    def select_output_dir(self):
        # Start file dialog in the current output directory
        start_dir = self.output_dir if os.path.exists(self.output_dir) else os.path.dirname(os.path.abspath(__file__))
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", start_dir)
        if directory:
            self.output_dir = directory
            self.output_dir_label.setText(f"Output: {directory}")

    def generate_images(self):
        if not self.input_image_path:
            QMessageBox.warning(self, "Warning", "Please drop an image first.")
            return
        # No need to check self.output_dir for None, as it's initialized
        # if not self.output_dir:
        #     QMessageBox.warning(self, "Warning", "Please select an output directory.")
        #     return

        selected_densities = [density for density, checkbox in self.density_checkboxes.items() if checkbox.isChecked()]
        if not selected_densities:
            QMessageBox.warning(self, "Warning", "Please select at least one target density.")
            return

        try:
            # --- Clear default output directory if it's selected ---
            if self.output_dir == self.default_output_dir:
                if os.path.exists(self.output_dir):
                    print(f"Clearing default output directory: {self.output_dir}")
                    shutil.rmtree(self.output_dir) # Remove the directory and its contents
                # No need to recreate immediately, makedirs later will handle it
                # os.makedirs(self.output_dir, exist_ok=True) # Recreate the base directory

            with Image.open(self.input_image_path) as img:
                original_width, original_height = img.size
                original_filename_base, original_ext = os.path.splitext(os.path.basename(self.input_image_path))

                # Density factors relative to xxxhdpi (4x) - Now includes xxxhdpi
                density_factors = {
                    "mdpi": 1.0 / 4.0,    # 1x / 4x
                    "hdpi": 1.5 / 4.0,    # 1.5x / 4x
                    "xhdpi": 2.0 / 4.0,   # 2x / 4x
                    "xxhdpi": 3.0 / 4.0,  # 3x / 4x
                    "xxxhdpi": 4.0 / 4.0  # 4x / 4x = 1.0
                }

                generated_count = 0
                errors = []
                for density in selected_densities:
                    try:
                        factor = density_factors[density]
                        target_width = int(round(original_width * factor)) # Use round for potentially better results
                        target_height = int(round(original_height * factor))

                        target_width = max(1, target_width)
                        target_height = max(1, target_height)

                        target_dir_name = f"drawable-{density}"
                        target_path = os.path.join(self.output_dir, target_dir_name)
                        # Create directory only when needed, handles base dir creation too
                        os.makedirs(target_path, exist_ok=True)

                        # Resize and save as PNG
                        resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                        output_filename = f"{original_filename_base}.png"
                        output_filepath = os.path.join(target_path, output_filename)

                        resized_img.save(output_filepath, 'PNG')
                        generated_count += 1
                    except Exception as e_inner:
                         error_msg = f"Error generating {density}: {e_inner}"
                         print(error_msg)
                         errors.append(error_msg)

                if not errors:
                     QMessageBox.information(self, "Success", f"Generated {generated_count} images successfully in '{self.output_dir}'.")
                else:
                     # Use a multi-line f-string for cleaner formatting
                     error_details = "\n".join(errors)
                     QMessageBox.warning(self, "Partial Success",
                                        f"Generated {generated_count} images, but encountered errors:\n{error_details}")

        except FileNotFoundError:
             QMessageBox.critical(self, "Error", f"Input image not found: {self.input_image_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during generation: {e}")
            print(f"Error details: {e}")


if __name__ == '__main__':
    # Ensure GUI scales well on high-DPI displays (optional but good practice)
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    ex = DensityGeneratorApp()
    ex.show()
    sys.exit(app.exec()) 
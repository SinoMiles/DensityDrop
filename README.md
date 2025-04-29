# DensityDrop

A simple Python utility to generate Android drawable resources for different densities from a single XXXHDPI source image.

## Features

*   Drag and drop an image file (assumed to be XXXHDPI).
*   Select target densities (MDPI, HDPI, XHDPI, XXHDPI, XXXHDPI).
*   Generates resized images into corresponding `drawable-*` folders.
*   Defaults to saving in a `generated_drawables` subfolder within the application directory.
*   Option to choose a custom output directory.
*   Clears the default output directory before each generation (if the default path is used).

## Requirements

*   Python 3.x
*   PyQt6
*   Pillow

## Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone https://github.com/SinoMiles/DensityDrop.git
    cd DensityDrop
    ```
2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```
2.  **Drag & Drop:** Drag your XXXHDPI source image onto the designated area in the application window.
3.  **Select Densities:** Ensure the checkboxes for the desired output densities are selected (defaults to all).
4.  **Select Output Directory (Optional):**
    *   By default, images are saved to a `generated_drawables` folder where the script is located. This folder is cleared before generation.
    *   Click "Select Output Directory" to choose a different location. Custom locations are *not* cleared automatically.
5.  **Generate:** Click the "Generate Images" button.

The generated images will be placed in subfolders like `drawable-mdpi`, `drawable-hdpi`, etc., within the chosen output directory. 
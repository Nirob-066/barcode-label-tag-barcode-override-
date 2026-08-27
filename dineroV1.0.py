"""
Dinero Barcode Placement Script (Version 1.0)
=============================================

This script automates the process of batch-placing barcode images onto a standard template.
It reads barcode images from a specified directory, resizes them according to configured
dimensions, and composites them onto a template image at precise coordinates. Finally, 
it outputs the finalized composited images as high-quality JPEGs.

Dependencies:
    - Pillow (PIL): Required for image processing operations.
    - tqdm: Required for displaying progress bars during batch processing.

Usage:
    Ensure 'template.png' or 'template.jpeg' is present in the configured `BASE_FOLDER`,
    and that barcodes are stored within `BASE_FOLDER/BARCODE_FOLDER_NAME`.
    Run the script via terminal: `python dineroV1.0.py`
"""

import os
from tqdm import tqdm
from PIL import Image

# IMPORTANT: This script requires Pillow (PIL) to be installed.
# Install with: pip install Pillow tqdm

# ============================================
# CONFIGURATION VARIABLES
# ============================================
BARCODE_FOLDER_NAME = 'barcode1'
WORK_FOLDER_NAME = 'work1'
BASE_FOLDER = '9'

# Barcode positioning and sizing (exact measurements from template)
BARCODE_WIDTH = 4610
BARCODE_HEIGHT = 1100
BARCODE_X = 2852
BARCODE_Y_FROM_BOTTOM = 3188

# Output quality
JPEG_QUALITY = 95
# ============================================

def print_header():
    """
    Displays a formatted, stylized header in the console upon execution.
    Utilizes ANSI escape codes to render the text in sky blue.
    """
    # Sky blue color
    color = '\033[96m'
    reset = '\033[0m'
    header = f"""
{color}
*************************************************
*                                               *
*         BARCODE PLACEMENT (Pure Python)       *
*                                               *
*************************************************
{reset}
"""
    print(header)

def read_file_names(directory="."):
    """
    Reads file names from a directory and returns them as a list.

    Args:
        directory: The path to the directory (default: current directory).

    Returns:
        A list of strings, where each string is a file name in the directory.
        Returns an empty list if the directory does not exist or if there are no files.
        Handles potential errors gracefully.
    """

    try:
        file_names = []
        # Iterate over all entries in the specified directory
        for filename in os.listdir(directory):
            # Construct the absolute path to verify the entry is a file (not a subdirectory)
            full_path = os.path.join(directory, filename)
            if os.path.isfile(full_path):
                # Filter files to include only supported image formats
                if filename.endswith('.jpeg') or filename.endswith('.png') or filename.endswith('.gif'):
                    file_names.append(filename)
        return file_names

    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")
        return []  # Return an empty list if the specified directory does not exist
    except Exception as e:
        # Catch and log any other potential filesystem errors (e.g., permission issues)
        print(f"An error occurred: {e}")
        return []

def generate_updated_images_pillow(
    barcodeName,
    actual_barcode_file_path,
    actual_work_folder_path,
    template_image
):
    """
    Processes a single barcode image, compositing it onto a base template using Pillow (PIL).
    The resulting composite image is then saved as a high-quality JPEG in the output folder.
    
    Args:
        barcodeName (str): The original filename of the barcode.
        actual_barcode_file_path (str): The absolute filesystem path to the barcode image.
        actual_work_folder_path (str): The filesystem path to the output directory.
        template_image (Image): The pre-loaded base template PIL Image object to paste onto.
    """
    if not os.path.exists(actual_barcode_file_path):
        return

    try:
        # Make a copy of the template for this barcode
        template_copy = template_image.copy()
        
        # Load and resize barcode image using configuration variables
        barcode = Image.open(actual_barcode_file_path)
        # Convert float dimensions to integers
        barcode_width_int = int(BARCODE_WIDTH)
        barcode_height_int = int(BARCODE_HEIGHT)
        barcode = barcode.resize((barcode_width_int, barcode_height_int), Image.LANCZOS)
        
        # Convert barcode to RGBA if it has transparency, otherwise RGB
        if barcode.mode in ('RGBA', 'LA') or (barcode.mode == 'P' and 'transparency' in barcode.info):
            barcode = barcode.convert('RGBA')
        else:
            barcode = barcode.convert('RGB')
        
        # Coordinate Transformation:
        # The design coordinates from Illustrator originated from the bottom-left corner,
        # but Pillow (PIL) uses a top-left coordinate system. We mathematically adjust the Y-coordinate.
        template_height = template_copy.height
        barcode_x_int = int(BARCODE_X)
        barcode_y_from_top = int(template_height - BARCODE_Y_FROM_BOTTOM - BARCODE_HEIGHT)
        
        # Paste barcode onto template
        if barcode.mode == 'RGBA':
            # Use alpha channel as mask for transparency
            template_copy.paste(barcode, (barcode_x_int, barcode_y_from_top), barcode)
        else:
            template_copy.paste(barcode, (barcode_x_int, barcode_y_from_top))
        
        # Save as JPEG
        barcodeNameWithoutExtention = os.path.splitext(barcodeName)[0]
        output_filename = f"{barcodeNameWithoutExtention}.jpeg"
        output_path = os.path.join(f"{actual_work_folder_path}_jpeg", output_filename)
        
        template_copy.save(output_path, 'JPEG', quality=JPEG_QUALITY)
        
    except Exception as e:
        print(f"\n\nError processing {barcodeName}: {e}")

def main():
    """
    Main orchestration function.
    Responsible for resolving directory paths, validating dependencies (like the template file),
    loading the template, and initializing the batch processing of barcode images.
    """
    print_header()

    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Build paths using configuration variables
    base_path = os.path.join(script_dir, BASE_FOLDER)
    actual_barcode_folder_path = os.path.join(base_path, BARCODE_FOLDER_NAME)
    actual_work_folder_path = os.path.join(base_path, WORK_FOLDER_NAME)
    
    # Template file path - now using PNG instead of SVG/AI
    template_png = os.path.join(base_path, 'template.png')
    template_jpeg = os.path.join(base_path, 'template.jpeg')

    # Check for template file (PNG or JPEG)
    actual_template_path = None
    if os.path.exists(template_png):
        actual_template_path = template_png
    elif os.path.exists(template_jpeg):
        actual_template_path = template_jpeg
    else:
        print(f"\n\nError: Neither 'template.png' nor 'template.jpeg' found in '{base_path}'")
        return

    print(f"Using template file: {actual_template_path}")
    print(f"Reading barcodes from: {actual_barcode_folder_path}")
    print(f"Outputting to: {actual_work_folder_path}_jpeg")

    # Load the template image into memory once to optimize batch processing
    try:
        template_image = Image.open(actual_template_path)
        # Convert the template to RGB mode if necessary to ensure it can be saved as a JPEG later
        if template_image.mode != 'RGB':
            template_image = template_image.convert('RGB')
        print(f"\nTemplate dimensions: {template_image.width}x{template_image.height}")
    except Exception as e:
        print(f"\nError loading template: {e}")
        return

    barcode_files = read_file_names(actual_barcode_folder_path)
    if not barcode_files:
        print(f"\n\nNo barcode image files found in '{actual_barcode_folder_path}'")
        return
    
    # Create the output directory if it doesn't exist
    os.makedirs(f"{actual_work_folder_path}_jpeg", exist_ok=True)

    print()  # Add blank line before progress bar
    
    # Initialize a progress bar for visual feedback during batch processing
    with tqdm(total=len(barcode_files), desc="Processing files", unit="file", ncols=100, leave=True) as pbar:
        for counter, file in enumerate(barcode_files, 1):
            actual_barcode_file_path = os.path.join(actual_barcode_folder_path, file)

            generate_updated_images_pillow(
                file,
                actual_barcode_file_path,
                actual_work_folder_path,
                template_image
            )
            
            pbar.set_postfix_str(f"{file}")
            pbar.update(1)
    
    print('\n\nFinished processing all files.')

if __name__ == "__main__":
    main()

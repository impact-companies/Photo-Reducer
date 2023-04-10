from PIL import Image
import os
import multiprocessing as mp
import pathlib
import time
import sys
from functools import partial
import glob

ACCEPTED_FILE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".JPG",
    ".JPEG"
)

# PIL JPEG variables
folder_path = ""
QUALITY_LEVEL = 50
REDUCTION_FACTOR = 2
BYTES_PER_KILO = 1000
MIN_IMAGE_WIDTH = 1080
MIN_IMAGE_HEIGHT = 1080
CPU_COUNT = 5

def reduce_file(file_path: str):
    try:
        image_file = Image.open(file_path)
        previous_size = os.stat(file_path).st_size / BYTES_PER_KILO
        image_width, image_height = image_file.size

        # Extract metadata to copy to new, saved image
        exif_data = image_file.info['exif']

        # Check if file still requires reduction
        if (image_width / REDUCTION_FACTOR < MIN_IMAGE_WIDTH and
        image_height / REDUCTION_FACTOR < MIN_IMAGE_HEIGHT):
            print(f"*  {file_path}:\tImage dimensions too small. Skipping...")
            return

        # Lower quality until optimal dimensions reached
        while (image_width / REDUCTION_FACTOR > MIN_IMAGE_WIDTH or
        image_height / REDUCTION_FACTOR > MIN_IMAGE_HEIGHT):
            image_file = image_file.reduce(REDUCTION_FACTOR)
            image_width, image_height = image_file.size

        # Save downsized image
        image_file.save(file_path, optimize=True, quality=QUALITY_LEVEL, exif=exif_data)
        current_size = os.stat(file_path).st_size / BYTES_PER_KILO
        print(f"*  {file_path}:\t{previous_size} KB ==> {current_size} KB")

    except Exception as e:
        print(e)

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        mp.freeze_support()

    accepted_files = []

    # Display some information
    print(f"""{'='*80}""")
    print("""
This program optimizes any photos in the JPEG file format within the given 
folder. Please be sure that you are providing the correct path.
    """)
    print(f"""{'='*80}""")

    folder_path = input("Path to folder: ")

    print(f"{'='*60}\nDetecting files...\n{'='*60}")
    
    for file in glob.glob(folder_path + "/**", recursive=True):
        if file.endswith(ACCEPTED_FILE_EXTENSIONS):
            accepted_files.append(file)
    
    print(f"{'='*60}")
    print("Files to be modified:")
    for file in accepted_files:
        print(file)
    input("Press enter to continue...")

    with mp.Pool(CPU_COUNT) as p:
        st = time.time()
        p.map(reduce_file, accepted_files)
        et = time.time()
    
    print(f"""{'='*60}""")
    print(f"Elapsed time: {(et-st)} seconds")
    print(f"""{'='*60}""")
    input("Press enter to exit...")

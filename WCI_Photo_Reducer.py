from PIL import Image
import os
import multiprocessing as mp
import pathlib
import time
import sys
from functools import partial

ACCEPTED_FILE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".JPG",
    ".JPEG"
}

# PIL JPEG variables
folder_path = ""
QUALITY_LEVEL = 50
REDUCTION_FACTOR = 2
BYTES_PER_KILO = 1000
MIN_IMAGE_WIDTH = 1080
MIN_IMAGE_HEIGHT = 1080
CPU_COUNT = 5

def reduce_file(dir_entry: str, folder_path: str):
    try:
        file_path = f"{folder_path}/{dir_entry}"
        image_file = Image.open(file_path)
        previous_size = os.stat(file_path).st_size / BYTES_PER_KILO
        image_width, image_height = image_file.size

        # Extract metadata to copy to new, saved image
        exif_data = image_file.info['exif']

        # Check if file still requires reduction
        if (image_width / REDUCTION_FACTOR < MIN_IMAGE_WIDTH and
        image_height / REDUCTION_FACTOR < MIN_IMAGE_HEIGHT):
            print(f"*  {dir_entry}:\tImage dimensions too small. Skipping...")
            return

        # Lower quality until optimal dimensions reached
        while (image_width / REDUCTION_FACTOR > MIN_IMAGE_WIDTH or
        image_height / REDUCTION_FACTOR > MIN_IMAGE_HEIGHT):
            image_file = image_file.reduce(REDUCTION_FACTOR)
            image_width, image_height = image_file.size

        # Save downsized image
        image_file.save(file_path, optimize=True, quality=QUALITY_LEVEL, exif=exif_data)
        current_size = os.stat(file_path).st_size / BYTES_PER_KILO
        print(f"*  {dir_entry}:\t{previous_size} KB ==> {current_size} KB")

    except Exception as e:
        print(e)

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        mp.freeze_support()

    skipped_files = []
    accepted_files = []

    # Display some information
    print(f"""{'='*80}""")
    print("""
This program optimizes any photos in the JPEG file format within the given 
folder. Please be sure that you are providing the correct path.
    """)
    print(f"""{'='*80}""")

    folder_path = input("Path to folder: ").replace("\\", "/")

    print(f"{'='*60}\nDetecting files...\n{'='*60}")
    for dir_entry in os.scandir(folder_path):
        file_path = f"{folder_path}/{dir_entry.name}"
        current_size = os.stat(file_path).st_size / BYTES_PER_KILO

        print(f"*  {dir_entry.name}\t{current_size} KB")
        
        # Check if file is directory
        if (dir_entry.is_dir()):
            skipped_files.append(dir_entry.name)
            continue

        # Check file extension
        file_extension = pathlib.Path(dir_entry).suffix
        if (file_extension not in ACCEPTED_FILE_EXTENSIONS):
            skipped_files.append(dir_entry.name)
            continue
        
        accepted_files.append(dir_entry.name)

    print(f"""\n{'='*60}\nFiles that will be skipped:\n{'-'*40}""")

    for entry in skipped_files:
        print(f"*  {entry}")

    print(f"""{'='*60}""")

    input("\nPress enter to begin...")

    print(f"\n{'='*60}\nProcessing files...\n{'-'*40}")

    with mp.Pool(CPU_COUNT) as p:
        pool_reduce = partial(reduce_file, folder_path=folder_path)
        st = time.time()
        p.map(pool_reduce, accepted_files)
        et = time.time()

    print(f"""{'='*60}""")
    print(f"""\n{'='*60}""")
    print(f"Elapsed time: {(et-st)} seconds")
    print(f"""{'='*60}""")
    input("Press enter to exit...")

"""
This module is meant to serve as an easy way to call a few functionalities of the main SISH repo
on external drives holding the data.
"""

import main_search
import search_adapter
from database import HistoDatabase
from path_validation_duplicate import validate_dir_for_patchify
import create_patches_fp
import os
import re
import shutil
import multiprocessing as mp
import extract_mosaic
import artifacts_removal

database: HistoDatabase = None
database_site: str = ""
data_path: str = ""


def main() -> None:
    global database

    while True:
        print("\n====SISH ADAPTER====")
        util_choice = input("Choose function ('ms' for main search, 'is' for individual search', "
                            "'p' to patchify, 'mo' for mosaic creation, 'e' to exit): ")

        if util_choice == 'ms':
            main_search_adapter()
        elif util_choice == 'is':
            individual_search_adapter()
        elif util_choice == 'p':
            patchify_adapter()
        elif util_choice == 'mo':
            mosaic_adapter()
        elif util_choice == 'e':
            if database:
                print("Freeing memory, this may take a little while...", flush=True)
                del database
            print("Exiting...", flush=True)
            return
        else:
            print("No such function exists")


def main_search_adapter() -> None:
    print("\n====MAIN SEARCH====")
    print("This will run a query for every single item in the database. That will take a long time.\n")
    update_site_and_database()

    main_search.run(database, database_site, data_path + "LATENT")


def individual_search_adapter() -> None:
    print("\n====INDIVIDUAL SEARCH====")
    print("Run a query for a specific item in the database.\n")
    update_site_and_database()

    latent_path: str = input("\n - Path (including filename) of the latent h5 file to query with: ")
    latent_path = latent_path.replace("\"", "") # Windows 'copy as path' sometimes inserts ", so get rid of those

    search_adapter.individual_search(database, database_site, latent_path)


def patchify_adapter() -> None:
    print("\n====PATCHIFY====")
    print("Patchify the wsi images in your database.\n")

    database_path = get_valid_wsi_path()
    if database_path == "None":
        return

    new_base_path = os.path.join(database_path, 'PATCHES')
    if os.path.exists(new_base_path):
        shutil.rmtree(new_base_path)
        print(f"Existing directory {new_base_path} removed")

    # Recreate directory structure under PATCHES
    mag_dir_pattern = re.compile(r"^\d+x$")
    for root, dirs, files in os.walk(database_path):
        head, tail = os.path.split(root)
        newtail = tail.replace('WSI', 'PATCHES')
        new_root = os.path.join(head,newtail)
        #new_root = root.replace('WSI', 'PATCHES')
        os.makedirs(new_root, exist_ok=True)

        # RUN PATCHIFY
        if mag_dir_pattern.match(os.path.basename(root)) and 'PATCHES' not in root:
            match = re.match(r"(\d+)x", os.path.basename(root))
            magnification_level = int(match.group(1))
            size = int(51.2 * magnification_level)

            print(f"\n\n\n------Starting patchify for {root} with size {size}------")
            create_patches_fp.process_images(source=root, save_dir=new_root, step_size=size, patch_size=size)


def mosaic_adapter() -> None:
    print("\n====MOSAIC CREATION====")
    print("Create mosaics out of your raw svs files and your patchified h5 files.\n")
    print("This step requires that you have done the patchify step already.")

    database_path = get_valid_wsi_path()
    if database_path == "None":
        return

    new_base_path = os.path.join(database_path, 'MOSAICS')
    if os.path.exists(new_base_path):
        shutil.rmtree(new_base_path)
        print(f"Existing directory {new_base_path} removed", flush=True)

    # MOSAIC CREATION
    mag_dir_pattern = re.compile(r"^\d+x$")
    num_cpu = mp.cpu_count()
    for root, dirs, files in os.walk(database_path):
        new_root = root.replace('WSI', 'MOSAICS')
        os.makedirs(new_root, exist_ok=True)

        # Run mosaic generation for each magnification subdirectory in the WSI path
        # ( And assume that an equivalent PATCHES path already exists)
        if mag_dir_pattern.match(os.path.basename(root)) and 'WSI' in root:
            slide_path = root
            patch_path = root.replace('WSI', 'PATCHES') + "/patches"
            if not os.listdir(patch_path):
                print(f"Skipping empty patch directory {patch_path}", flush=True)
                shutil.rmtree(new_root)
                continue

            os.makedirs(os.path.join(new_root, 'coord'), exist_ok=True)
            os.makedirs(os.path.join(new_root, 'coord_clean'), exist_ok=True)

            print(f"\n\n\n------Starting mosaic generation for {root}------", flush=True)
            extract_mosaic.process_slides(slide_path, patch_path, new_root, num_cpu)

    # ARTIFACT REMOVAL
    for site in os.listdir(new_base_path):
        path = os.path.join(new_base_path, site)
        print(f"\n\n\n------Starting artifact removal for {path}------", flush=True)
        artifacts_removal.process_mosaics(path.replace('MOSAICS', 'WSI'), path)


def get_valid_wsi_path() -> str:
    database_path: str = input(" - Path to your database folder: ").replace("\\", "/").replace("\"", "")
    validation_result = validate_dir_for_patchify(database_path)
    if not validation_result.is_valid:
        print(f"\n ERROR: {validation_result.failure_message}")
        return "None"
    if 'WSI' in database_path:
        print(f"\n ERROR: WSI selected instead of higher level DATABASE path")
        return "None"
    return database_path


def update_site_and_database():
    """
        Asks the user for the site they want to query in and makes the necessary updates to global variables
        (including the database)
    """
    global database, database_site

    temp_site: str = input(" - Site to search: ")
    update_database(temp_site)
    database_site = temp_site


def update_database(site: str) -> None:
    """
        Checks if the database needs to be rebuilt and if so, makes the necessary calls to do so.

        Args:
            site: The site the user intends to query in
    """

    global database, database_site

    if database and site == database_site:
        return

    if database and site != database_site:
        print("\nBecause you intend to query a new site, the database needs to be rebuilt")

    db_index_path, index_meta_path, codebook_semantic = update_data_paths(site)

    print("Building site specific database... \n(This will only need to run once if you intend "
          "to continue querying the same site. As long as you do not "
          "exit the program, the database will stay loaded for your next queries.)", flush=True)
    database = HistoDatabase(database_index_path=db_index_path,
                             index_meta_path=index_meta_path,
                             codebook_semantic=codebook_semantic)


def update_data_paths(site: str) -> tuple[str, str, str]:
    """
    Asks the user for the path to their data folder and then constructs the necessary path strings
    needed for calling the standard SISH functionalities.
    Also updates the global data_path variable.
    """

    print("\n**At this point you need to have a DATA folder that contains these directories: 'checkpoints', 'DATABASES'"
          " and 'LATENT'. Each should follow the structure described in the SISH readme**")
    path: str = input(" - Path to 'DATA': ")

    # Standardize the input
    path = standardize_path(path)
    if "DATA" not in path.upper():
        path += "DATA/"

    print(f"Registered path: {path}\n")

    # Construct path strings
    db_index_path = path + "DATABASES/" + site + "/index_tree/veb.pkl"
    index_meta_path = path + "DATABASES/" + site + "/index_meta/meta.pkl"
    codebook_semantic = path + "checkpoints/codebook_semantic.pt"

    global data_path
    data_path = path

    return db_index_path, index_meta_path, codebook_semantic


def standardize_path(path: str) -> str:
    path = path.replace("\"", "")
    path = path.replace("\\", "/")
    if path[len(path) - 1] != "/":
        path = path + "/"
    return path


if __name__ == "__main__":
    main()

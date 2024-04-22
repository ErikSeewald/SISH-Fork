"""
This module is meant to serve as an easy way to call a few functionalities of the main SISH repo
on external drives holding the data.
"""

import main_search
import search_adapter


def main():
    util_choice = input("Choose function ('ms' for main search, 'is' for individual search'): ")

    if util_choice == 'ms':
        main_search_adapter()
    elif util_choice == 'is':
        individual_search_adapter()
    else:
        print("No such function exists")


def get_data_paths(site: str) -> tuple[str, str, str, str]:

    """
    Asks the user for the path to their data folder and then constructs the necessary path strings
    needed for calling the standard SISH functionalities.
    """

    print("At this point you need to have a DATA folder that contains these directories: 'checkpoints', 'DATABASES'"
          " and 'LATENT'. Each should follow the structure described in the SISH readme")
    path: str = input("Path to 'DATA': ")

    # Standardize the input
    path = path.replace("\\", "/")
    if path[len(path) - 1] != "/":
        path = path + "/"

    if "DATA" not in path.upper():
        path += "DATA/"

    print(f"Registered path: {path}")

    # Construct path strings
    latent_path = path + "LATENT"
    db_index_path = path + "DATABASES/" + site + "/index_tree/veb.pkl"
    index_meta_path = path + "DATABASES/" + site + "/index_meta/meta.pkl"
    codebook_semantic = path + "checkpoints/codebook_semantic.pt"

    return latent_path, db_index_path, index_meta_path, codebook_semantic


def individual_search_adapter():
    print("\n====INDIVIDUAL SEARCH====")
    print("Run a query for a specific item in the database.")
    site: str = input("Site to search: ")

    _, db_index_path, index_meta_path, codebook_semantic = get_data_paths(site)
    latent: str = input("Path (including filename) of the latent h5 file to query with: ")
    search_adapter.individual_search(site, latent, db_index_path, index_meta_path, codebook_semantic)


def main_search_adapter():
    print("\n====MAIN SEARCH====")
    print("This will run a query for every single item in the database. That will take a long time.")
    site: str = input("Site to search: ")

    latent_path, db_index_path, index_meta_path, codebook_semantic = get_data_paths(site)
    main_search.run(latent_path, site, db_index_path, index_meta_path, codebook_semantic)


if __name__ == "__main__":
    main()

"""
This module is meant to serve as an easy way to call a few functionalities of the main SISH repo
on external drives holding the data.
"""

import main_search
import search_adapter
from database import HistoDatabase

database: HistoDatabase = None


def main() -> None:
    global database

    while True:
        print("\n====SISH ADAPTER====")
        util_choice = input("Choose function ('ms' for main search, 'is' for individual search', 'e' to exit): ")

        if util_choice == 'ms':
            main_search_adapter()
        elif util_choice == 'is':
            individual_search_adapter()
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
    site: str = input(" - Site to search: ")

    latent_path, db_index_path, index_meta_path, codebook_semantic = get_data_paths(site)
    build_database(db_index_path, index_meta_path, codebook_semantic)

    main_search.run(latent_path, site, database)


def individual_search_adapter() -> None:
    print("\n====INDIVIDUAL SEARCH====")
    print("Run a query for a specific item in the database.\n")
    site: str = input(" - Site to search: ")

    latent_path: str = input("\n - Path (including filename) of the latent h5 file to query with: ")
    latent_path = latent_path.replace("\"", "") # Windows 'copy as path' sometimes inserts ", so get rid of those

    if not database:
        _, db_index_path, index_meta_path, codebook_semantic = get_data_paths(site)
        build_database(db_index_path, index_meta_path, codebook_semantic)

    search_adapter.individual_search(site, latent_path, database)


def get_data_paths(site: str) -> tuple[str, str, str, str]:
    """
    Asks the user for the path to their data folder and then constructs the necessary path strings
    needed for calling the standard SISH functionalities.
    """

    print("\n**At this point you need to have a DATA folder that contains these directories: 'checkpoints', 'DATABASES'"
          " and 'LATENT'. Each should follow the structure described in the SISH readme**")
    path: str = input(" - Path to 'DATA': ")

    # Standardize the input
    path = path.replace("\"", "")
    path = path.replace("\\", "/")
    if path[len(path) - 1] != "/":
        path = path + "/"

    if "DATA" not in path.upper():
        path += "DATA/"

    print(f"Registered path: {path}\n")

    # Construct path strings
    latent_path = path + "LATENT"
    db_index_path = path + "DATABASES/" + site + "/index_tree/veb.pkl"
    index_meta_path = path + "DATABASES/" + site + "/index_meta/meta.pkl"
    codebook_semantic = path + "checkpoints/codebook_semantic.pt"

    return latent_path, db_index_path, index_meta_path, codebook_semantic


def build_database(db_index_path: str, index_meta_path: str, codebook_semantic: str) -> None:
    """
        Builds the latent code database out of prebuilt latent codes if it is not built already.

        Args:
            db_index_path: The path to the index_tree/veb.pkl of the site to search through
            index_meta_path: The path to the index_meta/meta.pkl of the site to search through
            codebook_semantic: The path to the checkpoints/codebook_semantic.pt
    """

    global database

    if database:
        return

    print("Building database... \n(This will only need to run once. As long as you do not "
          "exit the program, the database will stay loaded for your next queries.)", flush=True)
    database = HistoDatabase(database_index_path=db_index_path,
                             index_meta_path=index_meta_path,
                             codebook_semantic=codebook_semantic)


if __name__ == "__main__":
    main()

"""
This module is meant to serve as an easy way to call a few functionalities of the main SISH repo
on external drives holding the data.
"""

import main_search
import search_adapter
from database import HistoDatabase
import eval as eval_script

database: HistoDatabase = None
database_site: str = ""
data_path: str = ""


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
    update_site_and_database()

    main_search.run(database, database_site, data_path + "LATENT")


def individual_search_adapter() -> None:
    print("\n====INDIVIDUAL SEARCH====")
    print("Run a query for a specific item in the database.\n")
    update_site_and_database()

    latent_path: str = input("\n - Path (including filename) of the latent h5 file to query with: ")
    latent_path = latent_path.replace("\"", "") # Windows 'copy as path' sometimes inserts ", so get rid of those

    search_adapter.individual_search(database, database_site, latent_path)


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

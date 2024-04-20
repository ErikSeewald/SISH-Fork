import main_search


def main_search_adapter():
    print("\n====MAIN SEARCH====")
    site: str = input("Site to search: ")
    path: str = input("Path to './DATABASES/': ").replace("\\", "/")

    if path[len(path)-1] != "/":
        path = path + "/"

    if "DATABASES" not in path.upper():
        path += "DATABASES/"

    db_index_path = path + site + "/index_tree/veb.pkl"
    index_meta_path = path + site + "/index_meta/meta.pkl"
    main_search.run(site=site, db_index_path=db_index_path, index_meta_path=index_meta_path)


def main():
    util_choice = input("Choose function ('ms' for main search, ...): ")

    if util_choice == 'ms':
        main_search_adapter()
    else:
        print("No such function exists")


if __name__ == "__main__":
    main()

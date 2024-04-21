import argparse
import os
import pickle
import glob
from database import HistoDatabase
from tqdm import tqdm
import search_adapter


def run(latent_path="./DATA/LATENT", site=None,
        db_index_path=None, index_meta_path=None, codebook_semantic="./checkpoints/codebook_semantic.pt"):
    if site == 'organ':
        save_path = os.path.join("QUERY_RESULTS", site)
        latent_all = os.path.join(latent_path, "*", "*", "*", "vqvae", "*")
        speed_record_path = os.path.join("QUERY_SPEED", site)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if not os.path.exists(speed_record_path):
            os.makedirs(speed_record_path)
    else:
        save_path = os.path.join("QUERY_RESULTS", site)
        latent_all = os.path.join(latent_path, site,
                                  "*", "*", "vqvae", "*")
        speed_record_path = os.path.join("QUERY_SPEED", site)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if not os.path.exists(speed_record_path):
            os.makedirs(speed_record_path)

    db = HistoDatabase(database_index_path=db_index_path,
                       index_meta_path=index_meta_path,
                       codebook_semantic=codebook_semantic)
    results = {}
    for latent in tqdm(glob.glob(latent_all)):
        search_adapter.run_query(site, latent, db, speed_record_path, results)

    with open(os.path.join(save_path, "results.pkl"), 'wb') as handle:
        pickle.dump(results, handle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Search for WSI query in the database")
    parser.add_argument("--slide_path", type=str, default="./DATA/WSI",
                        help="The path to all slides")
    parser.add_argument("--latent_path", type=str, default="./DATA/LATENT",
                        help="The path to all mosaic latent code and text features")
    parser.add_argument("--site", type=str, required=True,
                        help="The site where the database is built")
    parser.add_argument("--db_index_path", type=str, required=True,
                        help="Path to the veb tree that stores all indices")
    parser.add_argument("--index_meta_path", type=str, required=True,
                        help="Path to the meta data of each index")
    parser.add_argument("--codebook_semantic", type=str, default="./checkpoints/codebook_semantic.pt", 
                        help="Path to the semantic codebook from vq-vae")
    args = parser.parse_args()

    # Changed so adapter files can run the functionality as well.
    run(args.latent_path, args.site, args.db_index_path,
        args.index_meta_path, args.codebook_semantic)

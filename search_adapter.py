"""
This module adapts some functionality formerly present in main_search.py
This lets us use the same code for multiple item and single item query.
"""

import time
import os
import h5py
import pickle
from database import HistoDatabase

# Slides which are in poor quality
IGNORE_SLIDES = ['TCGA-C5-A8YT-01Z-00-DX1.5609D977-4B7E-4B49-A3FB-50434D6E49F9',
                 'TCGA-06-1086-01Z-00-DX2.e1961f1f-a823-4775-acf7-04a46f05e15e',
                 'C3N-02678-21']


def run_query(site: str, latent_path: str, db: HistoDatabase, speed_record_path: str, results: dict) -> None:

    """
    Runs a single query for similar items to the item represented by the given latent code.

    Args:
        site: The physical site in the body of the whole slide image.
        latent_path: The path to the latent code of the item to query for.
        db: The prebuilt HistoDatabase.
        speed_record_path: The path to write the speed recording to.
        results: The dictionary to which the results should be written.
    """

    # Standardize latent path
    latent_path = latent_path.replace("\\", "/")
    print(f"\nRunning query on: {latent_path}", flush=True)

    # Extract info
    diagnosis = latent_path.split("/")[-4]
    anatomic_site = latent_path.split("/")[-5]

    # Ignore handling
    slide_id = os.path.basename(latent_path).replace(".h5", "")
    if slide_id in IGNORE_SLIDES:
        return

    # Remove the current patient from the database for leave-one-patient out evaluation
    # Implement your own to fit your own to fit your data.
    if not slide_id.startswith('TCGA'):
        # Implementation of your own leave-one out strategy to fit your data
        pass
    else:
        # Leave-one-patient out in TCGA cohort
        patient_id = slide_id.split("-")[2]
        db.leave_one_patient(patient_id)

    # Densefeat replacement
    densefeat_path = latent_path.replace("vqvae", "densenet").replace(".h5", ".pkl")
    with h5py.File(latent_path, 'r') as hf:
        feat = hf['features'][:]
    with open(densefeat_path, 'rb') as handle:
        densefeat = pickle.load(handle)

    # Query
    t_start = time.time()
    temp_results = []

    i = 0
    for idx, patch_latent in enumerate(feat):
        if i % 10 == 0:
            print(f"Processed {i} features...", flush=True)
        res = db.query(patch_latent, densefeat[idx])
        temp_results.append(res)
        i += 1

    # Write speed recording
    t_elapse = time.time() - t_start
    with open(os.path.join(speed_record_path, "speed_log.txt"), 'a') as fw:
        fw.write(slide_id + "," + str(t_elapse) + "\n")
    print(f"\nSearch took {t_elapse} seconds", flush=True)

    # Update results
    key = slide_id
    results[key] = {'results': None, 'label_query': None}
    results[key]['results'] = temp_results
    if site == 'organ':
        results[key]['label_query'] = anatomic_site
    else:
        results[key]['label_query'] = diagnosis


def individual_search(site: str, latent_path: str, database: HistoDatabase) -> None:
    """
    Builds the database and starts a query for an individual latent code wsi item.
    Then it writes the results and speed recording to the standard save path.

    Args:
        site: The physical site in the body of the whole slide image.
        latent_path: The path to the latent code of the item to query for.
        database: The database to search through
    """

    # Result and speed recording paths
    save_path = os.path.join("QUERY_RESULTS", site)
    speed_record_path = os.path.join("QUERY_SPEED", site)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(speed_record_path):
        os.makedirs(speed_record_path)

    # Run query
    results = {}
    run_query(site, latent_path, database, speed_record_path, results)

    # Save results
    print("Writing results to results.pkl...")
    with open(os.path.join(save_path, "results.pkl"), 'wb') as handle:
        pickle.dump(results, handle)

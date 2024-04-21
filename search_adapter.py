import time
import os
import h5py
import pickle
from database import HistoDatabase

# Slides which are in poor quality
IGNORE_SLIDES = ['TCGA-C5-A8YT-01Z-00-DX1.5609D977-4B7E-4B49-A3FB-50434D6E49F9',
                 'TCGA-06-1086-01Z-00-DX2.e1961f1f-a823-4775-acf7-04a46f05e15e',
                 'C3N-02678-21']


def run_query(site, latent, db, speed_record_path, results):

    """
    Runs a single query on the wsi of the given site represented by the specific latent code.
    Uses a prebuilt SISH database db.
    """
    latent = latent.replace("\\", "/")
    print(latent)
    diagnosis = latent.split("/")[-4]
    anatomic_site = latent.split("/")[-5]


    slide_id = os.path.basename(latent).replace(".h5", "")
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

    densefeat_path = latent.replace("vqvae", "densenet").replace(".h5", ".pkl")
    with h5py.File(latent, 'r') as hf:
        feat = hf['features'][:]
    with open(densefeat_path, 'rb') as handle:
        densefeat = pickle.load(handle)

    t_start = time.time()
    tmp_res = []
    for idx, patch_latent in enumerate(feat):
        res = db.query(patch_latent, densefeat[idx])
        tmp_res.append(res)
    t_elapse = time.time() - t_start
    with open(os.path.join(speed_record_path, "speed_log.txt"), 'a') as fw:
        fw.write(slide_id + "," + str(t_elapse) + "\n")
    print("Search takes ", t_elapse)

    key = slide_id
    results[key] = {'results': None, 'label_query': None}
    results[key]['results'] = tmp_res
    if site == 'organ':
        results[key]['label_query'] = anatomic_site
    else:
        results[key]['label_query'] = diagnosis


def individual_search(site, latent, db_index_path, index_meta_path, codebook_semantic):
    save_path = os.path.join("QUERY_RESULTS", site)
    speed_record_path = os.path.join("QUERY_SPEED", site)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(speed_record_path):
        os.makedirs(speed_record_path)

    db = HistoDatabase(database_index_path=db_index_path,
                       index_meta_path=index_meta_path,
                       codebook_semantic=codebook_semantic)
    results = {}
    run_query(site, latent, db, speed_record_path, results)

    with open(os.path.join(save_path, "results.pkl"), 'wb') as handle:
        pickle.dump(results, handle)

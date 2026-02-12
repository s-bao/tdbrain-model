import numpy as np
import pandas as pd
import pathlib
import matplotlib.pyplot as plt
from neurodsp.spectral import compute_spectrum
from neurodsp.plts.spectral import plot_power_spectra
import os
from joblib import Parallel, delayed
from tqdm import tqdm

# define file paths
eeg_path = '/oscar/data/sjones/shared/TDBRAIN_preprocessed/preprocessed'
metadata_path = '/oscar/home/scbao/tdbrain-model/data/TDBRAIN_participants_V2.tsv'
subj_list = os.listdir(eeg_path)

# read data
metadata_df = pd.read_csv(metadata_path, delimiter='\t')

# generate mask to pull out MDD, DISC subjects only
subj_mask = np.isin(metadata_df['participants_ID'].values, subj_list)
discovery_mask = metadata_df['DISC/REP'].values == 'DISCOVERY'
dataset_mask = metadata_df['Dataset'].values == 'MDD-rTMS'
rTMS_mask = ~metadata_df['rTMS PROTOCOL'].isna() # excludes 1 participant

mask = np.logical_and.reduce([subj_mask, discovery_mask, dataset_mask, rTMS_mask])

df = metadata_df[mask].copy() # .copy because plan to add columns later

# save paths to eeg numpy files for each subject in df
ec_eeg_path, eo_eeg_path, has_ses1 = list(), list(), list()

for subj_id in df['participants_ID'].values:
    subj_path = f'{eeg_path}/{subj_id}/ses-1/eeg'
    if os.path.isdir(subj_path):
        has_ses1.append(True)
        subj_files = os.listdir(subj_path)
        ec_subj_files = list(pathlib.Path(subj_path).glob('*restEC*.npy'))
        eo_subj_files = list(pathlib.Path(subj_path).glob('*restEO*.npy'))
        assert len(ec_subj_files) == len(eo_subj_files) == 1

        ec_eeg_path.append(str(ec_subj_files[0]))
        eo_eeg_path.append(str(eo_subj_files[0]))

    else:
        has_ses1.append(False)
        ec_eeg_path.append('')
        eo_eeg_path.append('')

df['ec_eeg_path'] = ec_eeg_path
df['eo_eeg_path'] = eo_eeg_path
df['has_ses1'] = has_ses1

# only keep subjects that have session 1 data
df = df[df['has_ses1'] == True].reset_index(drop=True)

# define feature extraction function
def get_bandpower_features(subj_data_path, condition, normalize=True):
    channel_filter = ['O1', 'O2', 'Pz', 'Fz', 'Cz'] # TODO: develop more robust way to choose channels

    eeg_dict = np.load(subj_data_path, allow_pickle=True)
    channel_labels = eeg_dict['labels']
    fs = eeg_dict['Fs']

    channel_mask = np.isin(channel_labels, channel_filter)
    eeg_data = eeg_dict['data'][0, channel_mask, :]
    # print(eeg_data.shape)
    assert eeg_data.shape[0] == len(channel_filter)

    bands = {
        'delta': [0.5, 4], 
        'theta': [4, 8], 
        'alpha': [8, 12], 
        'low_beta': [12, 20],
        'high_beta': [20, 30], 
        'low_gamma': [30, 40], 
        'high_gamma': [40, 80]
    }

    # construct dict with bandpower values for inputted subj
    feature_dict = {}

    for ch_idx, ch_name in enumerate(channel_filter):
        freqs, psd = compute_spectrum(eeg_data[ch_idx], fs, method='welch', avg_type='mean', nperseg=fs*2)
        
        band_powers = {}
        for band_name, (fmin, fmax) in bands.items():
            idx = (freqs >= fmin) & (freqs <= fmax)
            band_power = np.trapezoid(psd[idx], freqs[idx])
            band_powers[band_name] = band_power

        # normalize across all band powers for each channel
        if normalize:
            total_power = sum(band_powers.values()) + 1e-8
            for band_name in band_powers:
                band_powers[band_name] /= total_power

        for band_name, value in band_powers.items():
            feature_dict[f'{condition}_{ch_name}_{band_name}_power'] = value

    return feature_dict

def extract_subj_features(subj_id, ec_path, eo_path):
    feats = {'participants_ID': subj_id}
    feats.update(get_bandpower_features(ec_path, 'EC'))
    feats.update(get_bandpower_features(eo_path, 'EO'))
    return feats

# extract features in parallel for all subjects
res = Parallel(n_jobs=16)(
    delayed(extract_subj_features)(subj_id, ec_path, eo_path)
    for subj_id, ec_path, eo_path in tqdm(
        zip(df['participants_ID'].values,
            df['ec_eeg_path'].values,
            df['eo_eeg_path'].values),
        total=len(df)
    )
)

# save results in pickle file
bandpower_df = pd.DataFrame(res)
bandpower_df.to_pickle(f'../data/mdd_rtms_bandpower.pkl')




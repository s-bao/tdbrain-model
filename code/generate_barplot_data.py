import argparse
import json
import os
import pathlib
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from tqdm import tqdm

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT / "externals" / "DynaMix-python"))
TEST_SCORE_WIDE_FILENAME = "scores.csv"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "results" / "barplot_data"

ALL_CHANNELS_26 = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC3",
"FCz", "FC4", "T7", "C3", "Cz", "C4", "T8", "CP3", "CPz", "CP4", "P7", 
"P3", "Pz", "P4", "P8", "O1", "Oz", "O2"]

DEFAULT_MODELS = {
    "SimpleLogisticRegression": (
        LogisticRegression(solver="saga", class_weight="balanced", max_iter=1_000_000),
        {},
    ),
    "L1LogisticRegression": (
        LogisticRegression(solver="saga", class_weight="balanced", max_iter=1_000_000),
        {
            "logisticregression__C": [0.01, 0.1, 1, 10, 100],
            "logisticregression__l1_ratio": [1],
        },
    ),
    "L2LogisticRegression": (
        LogisticRegression(solver="saga", class_weight="balanced", max_iter=1_000_000),
        {
            "logisticregression__C": [0.0001, 0.001, 0.01, 0.1, 1],
            "logisticregression__l1_ratio": [0],
        },
    ),
    "ElasticNet": (
        LogisticRegression(solver="saga", class_weight="balanced", max_iter=100_000_000),
        {
            "logisticregression__C": [0.0001, 0.001, 0.01, 0.1, 1],
            "logisticregression__l1_ratio": [0.0001, 0.001, 0.01, 0.1, 1],
        },
    ),
    "SupportVectorClassifier": (
        SVC(probability=True),
        {
            "svc__C": [0.0001, 0.001, 0.01, 0.1, 1],
            "svc__gamma": [0.001, 0.01, 0.1],
            "svc__kernel": ["rbf"],
        },
    ),
}

BANDPOWER_BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 12),
    "low_beta": (12, 20),
    "high_beta": (20, 30),
    "low_gamma": (30, 40),
    "high_gamma": (40, 80),
}

FORECASTER = None
TORCH = None
DYNAMIX_FORECASTER_CLS = None
LOAD_HF_MODEL = None
NEURODSP_COMPUTE_SPECTRUM = None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train the same ML pipeline with demographic, DynaMix, or bandpower features."
    )
    parser.add_argument(
        "--output-dir",
        default="barplot_run",
        help="Output folder name under results/barplot_data, or an absolute directory path.",
    )
    parser.add_argument(
        "--condition",
        choices=["ec", "eo"],
        default="ec",
        help="Which EEG condition to featurize.",
    )
    parser.add_argument(
        "--feature-family",
        choices=["demographics_only", "dynamix", "bandpower"],
        required=True,
        help="Feature family to use.",
    )
    parser.add_argument(
        "--combo",
        action="append",
        default=[],
        help="Named channel combo as name=Ch1,Ch2,... Can be repeated.",
    )
    parser.add_argument(
        "--preset",
        action="append",
        default=[],
        choices=["all_channels", "original4ch"],
        help="Built-in channel combo presets. Can be repeated.",
    )
    parser.add_argument(
        "--dynamix-component",
        nargs="+",
        default=["w_exp", "mlp1", "mlp2", "model_out"],
        help="DynaMix components to include.",
    )
    parser.add_argument(
        "--embedding",
        nargs="+",
        default=["std", "mean"],
        choices=["std", "mean"],
        help="Summary embeddings to apply to each DynaMix component.",
    )
    parser.add_argument(
        "--bandpower-band",
        nargs="+",
        default=list(BANDPOWER_BANDS.keys()),
        choices=list(BANDPOWER_BANDS.keys()),
        help="Bandpower bands to include.",
    )
    parser.add_argument(
        "--bandpower-mode",
        choices=["separate", "all"],
        default="separate",
        help="Run bandpower one band at a time or combine all selected bands together.",
    )
    parser.add_argument(
        "--bandpower-normalize",
        action="store_true",
        help="Normalize each channel's bandpower by total power across the selected bands.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=list(DEFAULT_MODELS.keys()),
        choices=list(DEFAULT_MODELS.keys()),
        help="Models to evaluate inside the shared pipeline.",
    )
    parser.add_argument(
        "--num-states",
        type=int,
        default=100,
        help="Number of repeated train/test splits.",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=16,
        help="Parallel workers for feature extraction.",
    )
    parser.add_argument(
        "--corr-threshold",
        type=float,
        default=0.5,
        help="Correlation threshold for dropping redundant features.",
    )
    return parser.parse_args()


def sanitize_name(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def normalize_channels(channels):
    seen = set()
    normalized = []
    for channel in channels or []:
        if channel not in seen:
            normalized.append(channel)
            seen.add(channel)
    return normalized


def build_combo_map(args):
    if args.feature_family == "demographics_only":
        return {"demographics_only": []}

    combo_map = {}
    for preset in args.preset:
        if preset == "all_channels":
            combo_map["all_channels"] = ALL_CHANNELS_26[:]
        elif preset == "original4ch":
            combo_map["original4ch"] = ["F7", "P8", "T7", "O2"]

    for combo in args.combo:
        if "=" not in combo:
            raise ValueError(f"Invalid --combo value: {combo}")
        name, channel_str = combo.split("=", 1)
        channels = normalize_channels([ch.strip() for ch in channel_str.split(",") if ch.strip()])
        if not name.strip():
            raise ValueError(f"Invalid --combo value: {combo}")
        if not channels:
            raise ValueError(f"Combo {name} has no channels.")
        invalid_channels = [ch for ch in channels if ch not in ALL_CHANNELS_26]
        if invalid_channels:
            raise ValueError(f"Combo {name} has invalid channels: {invalid_channels}")
        combo_map[name.strip()] = channels

    if combo_map:
        return combo_map

    if args.feature_family in {"dynamix", "bandpower"}:
        raise ValueError(
            "--combo is required for --feature-family dynamix and bandpower"
        )
    return combo_map


def load_metadata():
    eeg_path = "/oscar/data/sjones/shared/TDBRAIN_preprocessed/preprocessed"
    metadata_path = REPO_ROOT / "data" / "TDBRAIN_participants_V2.tsv"
    subj_list = os.listdir(eeg_path)

    metadata_df = pd.read_csv(metadata_path, delimiter="\t")

    subj_mask = np.isin(metadata_df["participants_ID"].values, subj_list)
    discovery_mask = metadata_df["DISC/REP"].values == "DISCOVERY"
    dataset_mask = metadata_df["Dataset"].values == "MDD-rTMS"
    rtms_mask = ~metadata_df["rTMS PROTOCOL"].isna()
    mask = np.logical_and.reduce([subj_mask, discovery_mask, dataset_mask, rtms_mask])

    df = metadata_df[mask].copy()
    df["age"] = df["age"].str.replace(",", ".").astype(float)
    df = df.drop_duplicates(subset="participants_ID", keep="first")

    ec_eeg_path = []
    eo_eeg_path = []
    has_ses1 = []
    for subj_id in df["participants_ID"].values:
        subj_path = f"{eeg_path}/{subj_id}/ses-1/eeg"
        if os.path.isdir(subj_path):
            has_ses1.append(True)
            ec_subj_files = list(pathlib.Path(subj_path).glob("*restEC*.npy"))
            eo_subj_files = list(pathlib.Path(subj_path).glob("*restEO*.npy"))
            assert len(ec_subj_files) == len(eo_subj_files) == 1
            ec_eeg_path.append(str(ec_subj_files[0]))
            eo_eeg_path.append(str(eo_subj_files[0]))
        else:
            has_ses1.append(False)
            ec_eeg_path.append("")
            eo_eeg_path.append("")

    df["ec_eeg_path"] = ec_eeg_path
    df["eo_eeg_path"] = eo_eeg_path
    df["has_ses1"] = has_ses1
    df = df[df["has_ses1"]].reset_index(drop=True)
    return df


def ensure_forecaster():
    global FORECASTER, TORCH, DYNAMIX_FORECASTER_CLS, LOAD_HF_MODEL
    if FORECASTER is None:
        import torch
        from src.dynamix.model.forecaster import DynaMixForecaster
        from src.dynamix.utilities.utilities import load_hf_model

        TORCH = torch
        DYNAMIX_FORECASTER_CLS = DynaMixForecaster
        LOAD_HF_MODEL = load_hf_model

        model = LOAD_HF_MODEL("dynamix-6d-alrnn-v1.0")
        model.eval()
        FORECASTER = DYNAMIX_FORECASTER_CLS(model)
    return FORECASTER


def ensure_neurodsp_compute_spectrum():
    global NEURODSP_COMPUTE_SPECTRUM
    if NEURODSP_COMPUTE_SPECTRUM is None:
        from neurodsp.spectral import compute_spectrum

        NEURODSP_COMPUTE_SPECTRUM = compute_spectrum
    return NEURODSP_COMPUTE_SPECTRUM


def summarize_latent_array(array, embedding_name):
    array = np.asarray(array)
    # print("latent array:", array.shape)
    if embedding_name == "std":
        return np.std(array, axis=0)
    if embedding_name == "mean":
        return np.mean(array, axis=0)
    raise ValueError(f"Unsupported embedding: {embedding_name}")


def get_dynamix_feature_row(subj_data_path, channels, components, embeddings):
    '''
    components = wexp, mlp1, mlp2, modelout
    embeddings = mean, std
    '''
    forecaster = ensure_forecaster()
    torch = TORCH

    eeg_dict = np.load(subj_data_path, allow_pickle=True)
    channel_labels = eeg_dict["labels"]
    channel_mask = np.isin(channel_labels, channels)
    eeg_data = eeg_dict["data"][0, channel_mask, :]
    # print("eeg data:", eeg_data.shape)

    offset = 5000
    CL = 10000
    T = 1000

    context_start = offset
    context_end = offset + CL

    # Load the time series data
    ts_data = eeg_data.T

    context_ts = ts_data[context_start:context_end,:] # context from 5000 to 15000 (10s-30s)
    # print("context:", context_ts.shape)

    # Convert to PyTorch tensor
    context_ts_tensor = torch.tensor(context_ts, dtype=torch.float32)

    activation = {}
    # a dict to store the activations
    def getActivation(name):
        activation[name] = list()
        # the hook signature
        def hook(model, input, output):
            activation[name].append(output.detach())
        return hook

    hooks = [
        forecaster.model.gating_network.register_forward_hook(getActivation("w_exp")),
        forecaster.model.gating_network.mlp_layer1.register_forward_hook(getActivation("mlp1")),
        forecaster.model.gating_network.mlp_layer2.register_forward_hook(getActivation("mlp2")),
        forecaster.model.register_forward_hook(getActivation("model_out")),
    ]

    # Make prediction
    with torch.no_grad():
        forecaster.forecast(
            context=context_ts_tensor,
            horizon=T,
            preprocessing_method="pos_embedding",
            standardize=True,
            fit_nonstationary=False,
        )

    for h in hooks:
        h.remove()

    feature_names = []
    feature_values = []
    for component in components:
        component_array = torch.stack(activation[component]).numpy().squeeze()
  
        for embedding_name in embeddings:
            summary = summarize_latent_array(component_array, embedding_name)
            summary = np.asarray(summary)
            flat_values = summary.reshape(-1)

            if summary.ndim <= 1:
                names = [
                    f"dynamix_{component}_{embedding_name}_{i + 1}"
                    for i in range(flat_values.shape[0])
                ]
            else:
                names = []
                for idx in np.ndindex(summary.shape):
                    idx_label = "_".join(str(i + 1) for i in idx)
                    names.append(f"dynamix_{component}_{embedding_name}_{idx_label}")
            feature_names.extend(names)
            feature_values.append(flat_values)

    return np.concatenate(feature_values), feature_names


def get_dynamix_feature_values_only(subj_data_path, channels, components, embeddings):
    return get_dynamix_feature_row(
        subj_data_path=subj_data_path,
        channels=channels,
        components=components,
        embeddings=embeddings,
    )[0]


def summarize_bandpower_channel(psd, freqs, bands, normalize=False):
    band_powers = {}
    for band_name in bands:
        fmin, fmax = BANDPOWER_BANDS[band_name]
        idx = (freqs >= fmin) & (freqs <= fmax)
        band_powers[band_name] = float(np.trapezoid(psd[idx], freqs[idx]))

    if normalize:
        total_power = sum(band_powers.values()) + 1e-8
        return {band_name: value / total_power for band_name, value in band_powers.items()}

    return band_powers


def get_bandpower_feature_row(subj_data_path, condition, channels, bands, normalize=False):
    compute_spectrum = ensure_neurodsp_compute_spectrum()
    eeg_dict = np.load(subj_data_path, allow_pickle=True)
    channel_labels = eeg_dict["labels"]
    fs = float(eeg_dict["Fs"])
    channel_mask = np.isin(channel_labels, channels)
    eeg_data = eeg_dict["data"][0, channel_mask, :]
    selected_labels = channel_labels[channel_mask]

    feature_dict = {}
    for ch_idx, ch_name in enumerate(selected_labels):
        freqs, psd = compute_spectrum(
            eeg_data[ch_idx],
            fs,
            method="welch",
            avg_type="mean",
            nperseg=int(fs * 2),
        )
        band_powers = summarize_bandpower_channel(
            psd=psd,
            freqs=freqs,
            bands=bands,
            normalize=normalize,
        )
        for band_name, value in band_powers.items():
            feature_dict[f"{condition.upper()}_{ch_name}_{band_name}_power"] = value
    return feature_dict


def compute_or_load_dynamix_features(df, condition, channels, components, embeddings, cache_dir, n_jobs):
    cache_name = sanitize_name(
        f"dynamix_{condition}_{'_'.join(channels)}_{'_'.join(components)}_{'_'.join(embeddings)}"
    )
    cache_path = cache_dir / f"{cache_name}.pkl"
    if cache_path.exists():
        return pd.read_pickle(cache_path)

    paths = df[f"{condition}_eeg_path"].values
    first_features, feature_cols = get_dynamix_feature_row(
        paths[0],
        channels=channels,
        components=components,
        embeddings=embeddings,
    )
    remaining = Parallel(n_jobs=n_jobs)(
        delayed(get_dynamix_feature_values_only)(
            path,
            channels=channels,
            components=components,
            embeddings=embeddings,
        )
        for path in tqdm(paths[1:], desc="features:dynamix")
    )

    feature_array = np.vstack([first_features] + remaining)
    feature_df = pd.DataFrame(feature_array, columns=feature_cols)
    feature_df.insert(0, "participants_ID", df["participants_ID"].values)
    feature_df.to_pickle(cache_path)
    return feature_df


def compute_or_load_bandpower_features(
    df,
    condition,
    channels,
    bands,
    cache_dir,
    n_jobs,
    normalize,
):
    cache_suffix = "normalized" if normalize else "raw"
    cache_name = sanitize_name(
        f"bandpower_{condition}_{'_'.join(channels)}_{'_'.join(bands)}_{cache_suffix}"
    )
    cache_path = cache_dir / f"{cache_name}.pkl"
    if cache_path.exists():
        return pd.read_pickle(cache_path)

    rows = Parallel(n_jobs=n_jobs)(
        delayed(get_bandpower_feature_row)(
            row[f"{condition}_eeg_path"],
            condition=condition,
            channels=channels,
            bands=bands,
            normalize=normalize,
        )
        for row in tqdm(df.to_dict("records"), desc="features:bandpower")
    )
    feature_df = pd.DataFrame(rows)
    feature_df.insert(0, "participants_ID", df["participants_ID"].values)
    feature_df.to_pickle(cache_path)
    return feature_df


def remove_highly_correlated_columns(df, threshold=0.5, exclude_cols=None):
    exclude_cols = exclude_cols or []
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    if not feature_cols:
        return df, []
    corr = df[feature_cols].corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    cols_to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    return df.drop(columns=cols_to_drop), cols_to_drop


def nppv(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    denom_ppv = tp + fp
    percent_pos = np.mean(y_true == 1)
    if denom_ppv == 0 or percent_pos == 0:
        return 0
    ppv = tp / denom_ppv
    return (ppv / percent_pos) * 100


NPPV_SCORER = make_scorer(nppv)


def make_preprocessor(X):
    onehot_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant")),
            ("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore")),
        ]
    )
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_columns = ["gender"]
    numeric_columns = [col for col in X.columns if col not in categorical_columns]

    return ColumnTransformer(
        transformers=[
            ("onehot", onehot_transformer, categorical_columns),
            ("numeric", numeric_transformer, numeric_columns),
        ]
    )


def run_mlpipe(x_df, y, preprocessor, ml_algo, param_grid, num_states, progress_desc):
    raw_rows = []

    for split_idx in tqdm(
        range(num_states),
        desc=progress_desc,
        leave=False,
    ):
        random_state = 29 * (split_idx + 1)
        x_other, x_test, y_other, y_test = train_test_split(
            x_df, y, test_size=0.1, stratify=y, random_state=random_state
        )
        majority_class = Counter(y_test).most_common(1)[0][1]
        baseline_score = majority_class / len(y_test)

        kf = StratifiedKFold(n_splits=4, shuffle=True, random_state=random_state)
        pipeline = make_pipeline(preprocessor, ml_algo)
        grid = GridSearchCV(
            pipeline,
            param_grid=param_grid,
            cv=kf,
            scoring=NPPV_SCORER,
            return_train_score=True,
            n_jobs=-1,
            verbose=0,
        )
        grid.fit(x_other, y_other)

        best_model = grid.best_estimator_
        train_score = float(grid.cv_results_["mean_train_score"][grid.best_index_])
        test_score = float(nppv(y_test, best_model.predict(x_test)))

        raw_rows.append(
            {
                "split_idx": split_idx + 1,
                "random_state": random_state,
                "train_score": train_score,
                "test_score": test_score,
                "baseline_score": float(baseline_score),
                "best_params": json.dumps(grid.best_params_, sort_keys=True),
            }
        )

    raw_df = pd.DataFrame(raw_rows)
    summary = {
        "mean_train_score": float(raw_df["train_score"].mean()),
        "mean_test_score": float(raw_df["test_score"].mean()),
        "std_test_score": float(raw_df["test_score"].std(ddof=0)),
        "mean_baseline": float(raw_df["baseline_score"].mean()),
    }
    return summary, raw_df


def build_feature_frame(args, df, cache_dir, channels):
    if args.feature_family == "demographics_only":
        return df[["participants_ID"]].copy(), []

    if args.feature_family == "dynamix":
        feature_df = compute_or_load_dynamix_features(
            df=df,
            condition=args.condition,
            channels=channels,
            components=args.dynamix_component,
            embeddings=args.embedding,
            cache_dir=cache_dir,
            n_jobs=args.n_jobs,
        )
        feature_cols = [col for col in feature_df.columns if col != "participants_ID"]
        return feature_df, feature_cols

    feature_df = compute_or_load_bandpower_features(
        df=df,
        condition=args.condition,
        channels=channels,
        bands=args.bandpower_band,
        cache_dir=cache_dir,
        n_jobs=args.n_jobs,
        normalize=args.bandpower_normalize,
    )
    feature_cols = [col for col in feature_df.columns if col != "participants_ID"]
    return feature_df, feature_cols


def build_feature_subsets(args):
    if args.feature_family == "demographics_only":
        return [
            {
                "feature_subset": "demographics_only",
                "feature_cols": [],
                "dynamix_components": "",
                "embeddings": "",
                "bandpower_bands": "",
            }
        ]

    if args.feature_family == "dynamix":
        return [
            {
                "feature_subset": f"dynamix_{component}_{'_'.join(args.embedding)}",
                "feature_cols": [
                    f"dynamix_{component}_{embedding}_"
                    for embedding in args.embedding
                ],
                "dynamix_components": component,
                "embeddings": ",".join(args.embedding),
                "bandpower_bands": "",
            }
            for component in args.dynamix_component
        ]

    if args.bandpower_mode == "all":
        return [
            {
                "feature_subset": f"bandpower_{args.condition}_all",
                "feature_cols": args.bandpower_band[:],
                "dynamix_components": "",
                "embeddings": "",
                "bandpower_bands": ",".join(args.bandpower_band),
            }
        ]

    return [
        {
            "feature_subset": f"bandpower_{args.condition}_{band_name}",
            "feature_cols": [band_name],
            "dynamix_components": "",
            "embeddings": "",
            "bandpower_bands": band_name,
        }
        for band_name in args.bandpower_band
    ]


def select_feature_columns(args, feature_df, feature_subset, channels):
    if args.feature_family == "demographics_only":
        return []

    if args.feature_family == "dynamix":
        selected_cols = []
        for prefix in feature_subset["feature_cols"]:
            selected_cols.extend(feature_df.filter(regex=f"^{re.escape(prefix)}").columns.tolist())
        return selected_cols

    selected_cols = []
    condition_prefix = args.condition.upper()
    for channel in channels:
        for band_name in feature_subset["feature_cols"]:
            col = f"{condition_prefix}_{channel}_{band_name}_power"
            if col in feature_df.columns:
                selected_cols.append(col)
    return selected_cols


def evaluate_models(args, df, feature_df, combo_name, channels, feature_subsets):
    merged = pd.merge(feature_df, df, on="participants_ID", how="inner")
    demographic_cols = ["age", "gender", "BDI_pre"]
    y = merged["Remitter"].astype(float)
    raw_frames = []
    for feature_subset in feature_subsets:
        feature_cols = select_feature_columns(args, feature_df, feature_subset, channels)
        x_df = merged[demographic_cols + feature_cols].copy()
        x_df["gender"] = x_df["gender"].map({1.0: "male", 0.0: "female"})
        print(x_df.head(1))

        x_reduced, dropped_cols = remove_highly_correlated_columns(
            x_df,
            threshold=args.corr_threshold,
            exclude_cols=["gender"],
        )
        preprocessor = make_preprocessor(x_reduced)

        for model_name in tqdm(args.models, desc=f"models:{feature_subset['feature_subset']}"):
            algo, param_grid = DEFAULT_MODELS[model_name]
            _, raw_df = run_mlpipe(
                x_df=x_reduced,
                y=y,
                preprocessor=preprocessor,
                ml_algo=algo,
                param_grid=param_grid,
                num_states=args.num_states,
                progress_desc=f"splits:{model_name}",
            )
            common_fields = {
                "combo_name": combo_name,
                "feature_subset": feature_subset["feature_subset"],
                "model_name": model_name,
                "feature_family": args.feature_family,
                "condition": args.condition,
                "channels": ",".join(channels) if channels else np.nan,
                "dynamix_components": feature_subset["dynamix_components"],
                "embeddings": feature_subset["embeddings"],
                "bandpower_bands": feature_subset["bandpower_bands"],
                "bandpower_normalize": bool(args.bandpower_normalize) if args.feature_family == "bandpower" else "",
                "n_subjects": int(len(merged)),
                "n_input_features_pre_corr": int(x_df.shape[1]),
                "n_input_features_post_corr": int(x_reduced.shape[1]),
                "n_dropped_corr_features": int(len(dropped_cols)),
            }
            raw_frames.append(raw_df.assign(**common_fields))

    return pd.concat(raw_frames, ignore_index=True)


def resolve_output_dir(output_dir_arg):
    output_dir = pathlib.Path(output_dir_arg)
    if output_dir.is_absolute():
        return output_dir
    return DEFAULT_OUTPUT_ROOT / output_dir


def build_test_score_wide_table(raw_df, source_run):
    long_df = raw_df.rename(
        columns={
            "train_score": "state_train_score",
            "test_score": "state_test_score",
        }
    ).copy()
    long_df.insert(0, "source_run", source_run)

    index_cols = ["source_run", "combo_name", "feature_subset", "random_state"]
    metadata_cols = [
        "channels",
        "n_input_features_pre_corr",
        "n_input_features_post_corr",
    ]
    score_frames = []
    for value_col, suffix in [
        ("state_train_score", "train_score"),
        ("state_test_score", "test_score"),
    ]:
        score_df = (
            long_df.pivot(
                index=index_cols,
                columns="model_name",
                values=value_col,
            )
            .reset_index()
            .sort_values(index_cols)
            .reset_index(drop=True)
        )
        rename_map = {
            col: f"{col}_{suffix}"
            for col in score_df.columns
            if col not in index_cols
        }
        score_frames.append(score_df.rename(columns=rename_map))

    wide_df = score_frames[0]
    for score_df in score_frames[1:]:
        wide_df = wide_df.merge(score_df, on=index_cols, how="outer")

    metadata_df = (
        long_df[index_cols + metadata_cols]
        .drop_duplicates()
        .sort_values(index_cols)
        .reset_index(drop=True)
        .rename(
            columns={
                "n_input_features_pre_corr": "n_features_pre_corr",
                "n_input_features_post_corr": "n_features_post_corr",
            }
        )
    )
    wide_df = metadata_df.merge(wide_df, on=index_cols, how="left")

    return wide_df.sort_values(index_cols).reset_index(drop=True)


def main():
    args = parse_args()
    combo_map = build_combo_map(args)
    feature_subsets = build_feature_subsets(args)

    output_dir = resolve_output_dir(args.output_dir).resolve()
    run_name = output_dir.name
    cache_dir = output_dir / "cache"
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    print("Loading metadata...")
    df = load_metadata()

    raw_frames = []
    for combo_name, channels in combo_map.items():
        print(f"Building {args.feature_family} features for {combo_name}...")
        feature_df, _ = build_feature_frame(args, df, cache_dir, channels)
        print(feature_df.head())

        print(f"Training models for {combo_name}...")
        raw_frames.append(
            evaluate_models(args, df, feature_df, combo_name, channels, feature_subsets)
        )

    raw_df = pd.concat(raw_frames, ignore_index=True)
    wide_df = build_test_score_wide_table(
        raw_df=raw_df,
        source_run=run_name,
    )

    wide_csv = output_dir / TEST_SCORE_WIDE_FILENAME
    config_json = output_dir / "config.json"

    wide_df.to_csv(wide_csv, index=False)
    config_json.write_text(
        json.dumps(
            {
                "feature_family": args.feature_family,
                "condition": args.condition,
                "combos": combo_map,
                "dynamix_components": args.dynamix_component,
                "embeddings": args.embedding,
                "bandpower_bands": args.bandpower_band,
                "bandpower_normalize": args.bandpower_normalize,
                "models": args.models,
                "num_states": args.num_states,
                "n_jobs": args.n_jobs,
                "corr_threshold": args.corr_threshold,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nSaved:")
    print(wide_csv)
    print(config_json)


if __name__ == "__main__":
    main()

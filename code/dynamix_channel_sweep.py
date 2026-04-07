import argparse
import json
import os
import pathlib
import re
import sys
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
import torch
from joblib import Parallel, delayed
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from tqdm import tqdm

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT / "externals" / "DynaMix-python"))

from src.dynamix.model.forecaster import DynaMixForecaster
from src.dynamix.utilities.utilities import load_hf_model


ALL_CHANNELS_26 = [
    "Fp1",
    "Fp2",
    "F7",
    "F3",
    "Fz",
    "F4",
    "F8",
    "FC3",
    "FCz",
    "FC4",
    "T7",
    "C3",
    "Cz",
    "C4",
    "T8",
    "CP3",
    "CPz",
    "CP4",
    "P7",
    "P3",
    "Pz",
    "P4",
    "P8",
    "O1",
    "Oz",
    "O2",
]

# REGIONS = {
#     "frontal": ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"],
#     "frontocentral": ["FC3", "FCz", "FC4"],
#     "central": ["C3", "Cz", "C4", "T7", "T8"],
#     "parietal": ["CP3", "CPz", "CP4", "P7", "P3", "Pz", "P4", "P8"],
#     "occipital": ["O1", "Oz", "O2"],
# }

REGIONS = {
    "frontal": ["F7", "F3", "Fz", "F4", "F8"],
    "frontocentral": ["FC3", "FCz", "FC4"],
    "central": ["C3", "Cz", "C4"],
    "parietal": ["P7", "P3", "Pz", "P4", "P8"],
    "occipital": ["O1", "Oz", "O2"],
}

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

FORECASTER = None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the DynaMix pipeline across multiple channel combinations."
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "results" / "dynamix_channel_sweeps"),
        help="Directory for sweep outputs.",
    )
    parser.add_argument(
        "--condition",
        choices=["ec", "eo"],
        default="ec",
        help="Which EEG condition to featurize. Default matches the current notebook flow.",
    )
    parser.add_argument(
        "--response-var",
        default="Remitter",
        help="Outcome column in the metadata dataframe.",
    )
    parser.add_argument(
        "--eval-metric",
        choices=["nppv", "accuracy", "precision", "f1_macro", "f1_weighted"],
        default="nppv",
        help="Model selection and holdout scoring metric.",
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
    parser.add_argument(
        "--preset",
        action="append",
        default=[],
        choices=[
            "brain_areas",
            "original_4ch",
            "all_channels",
            "single_channels",
            "leave_one_region_out",
        ],
        help="Built-in channel combination presets. Can be repeated.",
    )
    parser.add_argument(
        "--combo",
        action="append",
        default=[],
        help="Custom channel combo as name=Ch1,Ch2,... Can be repeated.",
    )
    parser.add_argument(
        "--combo-json",
        default=None,
        help="Optional JSON file mapping combo names to channel lists.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=list(DEFAULT_MODELS.keys()),
        choices=list(DEFAULT_MODELS.keys()),
        help="Subset of models to run.",
    )
    parser.add_argument(
        "--force-recompute",
        action="store_true",
        help="Ignore cached features and recompute.",
    )
    parser.add_argument(
        "--demographics-only",
        action="store_true",
        help="Skip DynaMix feature extraction and run models using demographic features only.",
    )
    parser.add_argument(
        "--append-existing",
        action="store_true",
        help="Merge this run into existing results in --output-dir instead of replacing them.",
    )
    parser.add_argument(
        "--run-tag",
        default=None,
        help="Label for this run when using --append-existing. Defaults to a timestamp.",
    )
    return parser.parse_args()


def sanitize_name(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def resolve_run_tag(args):
    if args.run_tag:
        return sanitize_name(args.run_tag)
    if args.append_existing:
        return datetime.now().strftime("run_%Y%m%d_%H%M%S")
    return sanitize_name(pathlib.Path(args.output_dir).resolve().name)


def build_combo_map(args):
    combo_map = {}

    if args.demographics_only:
        return {"demographics_only": []}

    if not args.preset and not args.combo and not args.combo_json:
        combo_map.update({name: channels[:] for name, channels in REGIONS.items()})

    for preset in args.preset:
        if preset == "brain_areas":
            combo_map.update({name: channels[:] for name, channels in REGIONS.items()})
        elif preset == "original_4ch":
            combo_map["original_4ch"] = ["F7", "P8", "T7", "O2"]
        elif preset == "all_channels":
            combo_map["all_26ch"] = ALL_CHANNELS_26[:]
        elif preset == "single_channels":
            for channel in ALL_CHANNELS_26:
                combo_map[f"single_{channel}"] = [channel]
        elif preset == "leave_one_region_out":
            for region_name, region_channels in REGIONS.items():
                combo_map[f"all_except_{region_name}"] = [
                    ch for ch in ALL_CHANNELS_26 if ch not in region_channels
                ]

    for combo in args.combo:
        if "=" not in combo:
            raise ValueError(f"Invalid --combo value: {combo}")
        name, channel_str = combo.split("=", 1)
        channels = [ch.strip() for ch in channel_str.split(",") if ch.strip()]
        if not channels:
            raise ValueError(f"Combo {name} has no channels.")
        combo_map[name.strip()] = channels

    if args.combo_json:
        with open(args.combo_json, "r", encoding="utf-8") as handle:
            file_combos = json.load(handle)
        for name, channels in file_combos.items():
            combo_map[name] = list(channels)

    if not combo_map:
        raise ValueError("No channel combinations were specified.")

    invalid = {
        name: [ch for ch in channels if ch not in ALL_CHANNELS_26]
        for name, channels in combo_map.items()
    }
    invalid = {name: bad for name, bad in invalid.items() if bad}
    if invalid:
        raise ValueError(f"Found invalid channel names: {invalid}")

    deduped = {}
    for name, channels in combo_map.items():
        seen = set()
        unique_channels = []
        for ch in channels:
            if ch not in seen:
                unique_channels.append(ch)
                seen.add(ch)
        deduped[name] = unique_channels
    return deduped


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
    global FORECASTER
    if FORECASTER is None:
        model = load_hf_model("dynamix-6d-alrnn-v1.0")
        model.eval()
        FORECASTER = DynaMixForecaster(model)
    return FORECASTER


def get_dynamix_latent(subj_data_path, channel_filter, horizon=100):
    forecaster = ensure_forecaster()

    eeg_dict = np.load(subj_data_path, allow_pickle=True)
    channel_labels = eeg_dict["labels"]
    channel_mask = np.isin(channel_labels, channel_filter)
    eeg_data = eeg_dict["data"][0, channel_mask, :]
    assert eeg_data.shape[0] == len(channel_filter), (
        f"Expected {len(channel_filter)} channels, got {eeg_data.shape[0]} "
        f"for {subj_data_path} with filter {channel_filter}"
    )

    offset = 5000
    context_length = 10000
    context_ts = eeg_data.T[offset : offset + context_length, :]
    context_ts_tensor = torch.tensor(context_ts, dtype=torch.float32)

    activation = {}

    def capture(name):
        activation[name] = []

        def hook(model, inputs, output):
            activation[name].append(output.detach())

        return hook

    hooks = [
        forecaster.model.gating_network.register_forward_hook(capture("w_exp")),
        forecaster.model.gating_network.mlp_layer1.register_forward_hook(capture("mlp1")),
        forecaster.model.gating_network.mlp_layer2.register_forward_hook(capture("mlp2")),
        forecaster.model.register_forward_hook(capture("model_out")),
    ]

    with torch.no_grad():
        forecaster.forecast(
            context=context_ts_tensor,
            horizon=horizon,
            preprocessing_method="pos_embedding",
            standardize=True,
            fit_nonstationary=False,
        )

    for hook in hooks:
        hook.remove()

    w_exp = torch.stack(activation["w_exp"]).numpy().squeeze()
    mlp1 = torch.stack(activation["mlp1"]).numpy().squeeze()
    mlp2 = torch.stack(activation["mlp2"]).numpy().squeeze()
    model_out = torch.stack(activation["model_out"]).numpy().squeeze()

    feature_names = []
    feature_values = []
    for prefix, array in [
        ("wexp", w_exp),
        ("mlp1", mlp1),
        ("mlp2", mlp2),
        ("modelout", model_out),
    ]:
        for stat_name, summary in [
            ("std", np.std(array, axis=0)),
            ("mean", np.mean(array, axis=0)),
        ]:
            summary = np.asarray(summary)
            flat_values = summary.reshape(-1)
            if summary.ndim <= 1:
                names = [
                    f"dynamix_{prefix}_{stat_name}_{i + 1}"
                    for i in range(flat_values.shape[0])
                ]
            else:
                names = []
                for idx in np.ndindex(summary.shape):
                    idx_label = "_".join(str(i + 1) for i in idx)
                    names.append(f"dynamix_{prefix}_{stat_name}_{idx_label}")
            feature_names.extend(names)
            feature_values.append(flat_values)

    return np.concatenate(feature_values), feature_names


def get_dynamix_latent_values_only(subj_data_path, channel_filter, horizon=100):
    return get_dynamix_latent(
        subj_data_path=subj_data_path,
        channel_filter=channel_filter,
        horizon=horizon,
    )[0]


def compute_or_load_features(df, combo_name, channels, condition, cache_dir, n_jobs, force_recompute):
    cache_name = sanitize_name(f"{combo_name}_{condition}")
    cache_path = cache_dir / f"{cache_name}_features.pkl"

    if cache_path.exists() and not force_recompute:
        return pd.read_pickle(cache_path)

    paths = df[f"{condition}_eeg_path"].values
    first_features, feature_cols = get_dynamix_latent(paths[0], channels)
    remaining = Parallel(n_jobs=n_jobs)(
        delayed(get_dynamix_latent_values_only)(path, channels)
        for path in tqdm(paths[1:], desc=f"features:{combo_name}")
    )

    feature_array = np.vstack([first_features] + remaining)
    feature_df = pd.DataFrame(feature_array, columns=feature_cols)
    feature_df.insert(0, "participants_ID", df["participants_ID"].values)
    feature_df.to_pickle(cache_path)
    return feature_df


def build_demographics_only_features(df):
    return df[["participants_ID"]].copy()


def remove_highly_correlated_columns(df, threshold=0.5, exclude_cols=None):
    exclude_cols = exclude_cols or []
    feature_cols = [c for c in df.columns if c not in exclude_cols]
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
            ("imputer0", SimpleImputer(strategy="constant")),
            ("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore")),
        ]
    )
    numeric_transformer = Pipeline(
        steps=[
            ("imputer2", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    dynamix_cols = X.filter(regex="dynamix_").columns.tolist()
    onehot_ftrs = ["gender"]
    std_ftrs = ["age", "BDI_pre"] + dynamix_cols

    return ColumnTransformer(
        transformers=[
            ("onehot", onehot_transformer, onehot_ftrs),
            ("std", numeric_transformer, std_ftrs),
        ]
    )


def run_mlpipe(x_df, y, preprocessor, ml_algo, param_grid, eval_metric, num_states):
    train_scores = []
    test_scores = []
    baseline_scores = []

    for i in range(num_states):
        random_state = 29 * (i + 1)
        x_other, x_test, y_other, y_test = train_test_split(
            x_df, y, test_size=0.1, stratify=y, random_state=random_state
        )
        majority_class = Counter(y_test).most_common(1)[0][1]
        baseline_scores.append(majority_class / len(y_test))

        kf = StratifiedKFold(n_splits=4, shuffle=True, random_state=random_state)
        pipeline = make_pipeline(preprocessor, ml_algo)
        scoring_func = NPPV_SCORER if eval_metric == "nppv" else eval_metric

        grid = GridSearchCV(
            pipeline,
            param_grid=param_grid,
            cv=kf,
            scoring=scoring_func,
            return_train_score=True,
            n_jobs=-1,
            verbose=0,
        )
        grid.fit(x_other, y_other)

        best_model = grid.best_estimator_
        train_scores.append(grid.cv_results_["mean_train_score"][grid.best_index_])

        y_test_pred = best_model.predict(x_test)
        if eval_metric == "accuracy":
            test_score = accuracy_score(y_test, y_test_pred)
        elif eval_metric == "precision":
            test_score = precision_score(y_test, y_test_pred, average="macro")
        elif eval_metric == "f1_macro":
            test_score = f1_score(y_test, y_test_pred, average="macro")
        elif eval_metric == "f1_weighted":
            test_score = f1_score(y_test, y_test_pred, average="weighted")
        elif eval_metric == "nppv":
            test_score = nppv(y_test, y_test_pred)
        else:
            raise ValueError(f"Unhandled eval metric: {eval_metric}")
        test_scores.append(test_score)

    return {
        "mean_train_score": float(np.mean(train_scores)),
        "mean_test_score": float(np.mean(test_scores)),
        "std_test_score": float(np.std(test_scores)),
        "mean_baseline": float(np.mean(baseline_scores)),
    }


def evaluate_combo(
    df,
    feature_df,
    combo_name,
    channels,
    response_var,
    eval_metric,
    models,
    corr_threshold,
    num_states,
):
    merged = pd.merge(feature_df, df, on="participants_ID", how="inner")
    cols = ["age", "gender", "BDI_pre"]
    dynamix_cols = merged.filter(regex="dynamix_wexp_std").columns.tolist()

    x_df = merged[cols + dynamix_cols].copy()
    y = merged[response_var].astype(float)
    x_df["gender"] = x_df["gender"].map({1.0: "male", 0.0: "female"})

    x_reduced, dropped_cols = remove_highly_correlated_columns(
        x_df,
        threshold=corr_threshold,
        exclude_cols=["participants_ID", "gender"],
    )
    preprocessor = make_preprocessor(x_reduced)

    rows = []
    for model_name, (algo, param_grid) in models.items():
        scores = run_mlpipe(
            x_df=x_reduced,
            y=y,
            preprocessor=preprocessor,
            ml_algo=algo,
            param_grid=param_grid,
            eval_metric=eval_metric,
            num_states=num_states,
        )
        rows.append(
            {
                "combo_name": combo_name,
                "channels": ",".join(channels),
                "n_channels": len(channels),
                "feature_set": "demographics_only" if not dynamix_cols else "demographics_plus_dynamix",
                "model_name": model_name,
                "response_var": response_var,
                "eval_metric": eval_metric,
                "n_subjects": int(len(merged)),
                "n_input_features_pre_corr": int(x_df.shape[1]),
                "n_input_features_post_corr": int(x_reduced.shape[1]),
                "n_dropped_corr_features": int(len(dropped_cols)),
                **scores,
            }
        )
    return pd.DataFrame(rows)


def write_markdown_summary(results_df, combo_df, output_path):
    def dataframe_to_markdown(df):
        df = df.copy()
        headers = list(df.columns)
        rows = [[str(value) for value in row] for row in df.itertuples(index=False, name=None)]
        widths = []
        for col_idx, header in enumerate(headers):
            cell_width = max([len(header)] + [len(row[col_idx]) for row in rows]) if rows else len(header)
            widths.append(cell_width)

        def format_row(values):
            return "| " + " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(values)) + " |"

        separator = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
        lines = [format_row(headers), separator]
        lines.extend(format_row(row) for row in rows)
        return "\n".join(lines)

    lines = []
    lines.append("# DynaMix Channel Sweep Summary")
    lines.append("")
    lines.append("## Best Model Per Channel Set")
    lines.append("")
    best_columns = [
        "source_run",
        "combo_name",
        "channels",
        "n_channels",
        "model_name",
        "mean_test_score",
        "std_test_score",
        "mean_baseline",
    ]
    best_columns = [col for col in best_columns if col in combo_df.columns]
    lines.append(dataframe_to_markdown(combo_df[best_columns]))
    lines.append("")
    lines.append("## Full Results")
    lines.append("")
    full_columns = [
        "source_run",
        "combo_name",
        "model_name",
        "mean_test_score",
        "std_test_score",
        "mean_train_score",
        "mean_baseline",
        "n_input_features_post_corr",
    ]
    full_columns = [col for col in full_columns if col in results_df.columns]
    sort_columns = [col for col in ["source_run", "combo_name"] if col in results_df.columns]
    sort_columns.append("mean_test_score")
    ascending = [True] * (len(sort_columns) - 1) + [False]
    lines.append(
        dataframe_to_markdown(
            results_df.sort_values(sort_columns, ascending=ascending)[full_columns]
        )
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def load_existing_results(results_csv, fallback_source_run):
    if not results_csv.exists():
        return None

    existing_df = pd.read_csv(results_csv)
    if "source_run" not in existing_df.columns:
        existing_df.insert(0, "source_run", fallback_source_run)
    return existing_df


def build_aggregate_tables(results_df):
    group_cols = ["combo_name"]
    sort_cols = ["combo_name", "mean_test_score"]
    ascending = [True, False]

    if "source_run" in results_df.columns:
        group_cols = ["source_run", "combo_name"]
        sort_cols = ["source_run", "combo_name", "mean_test_score"]
        ascending = [True, True, False]

    combo_best_df = (
        results_df.sort_values(sort_cols, ascending=ascending)
        .groupby(group_cols, as_index=False)
        .first()
        .sort_values(["mean_test_score", "std_test_score"], ascending=[False, True])
        .reset_index(drop=True)
    )

    pivot_index = group_cols if len(group_cols) > 1 else group_cols[0]
    pivot_df = results_df.pivot(
        index=pivot_index, columns="model_name", values="mean_test_score"
    ).sort_index()

    return combo_best_df, pivot_df


def main():
    args = parse_args()
    combo_map = build_combo_map(args)
    run_tag = resolve_run_tag(args)

    output_dir = pathlib.Path(args.output_dir).resolve()
    cache_dir = output_dir / "cache"
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading metadata for {len(combo_map)} channel combinations...")
    df = load_metadata()

    selected_models = {name: DEFAULT_MODELS[name] for name in args.models}
    results_frames = []

    for combo_name, channels in combo_map.items():
        print(f"\n=== {combo_name} | {channels} ===")
        if args.demographics_only:
            feature_df = build_demographics_only_features(df)
        else:
            feature_df = compute_or_load_features(
                df=df,
                combo_name=combo_name,
                channels=channels,
                condition=args.condition,
                cache_dir=cache_dir,
                n_jobs=args.n_jobs,
                force_recompute=args.force_recompute,
            )
        combo_results = evaluate_combo(
            df=df,
            feature_df=feature_df,
            combo_name=combo_name,
            channels=channels,
            response_var=args.response_var,
            eval_metric=args.eval_metric,
            models=selected_models,
            corr_threshold=args.corr_threshold,
            num_states=args.num_states,
        )
        results_frames.append(combo_results)

    current_results_df = pd.concat(results_frames, ignore_index=True)
    current_results_df.insert(0, "source_run", run_tag)
    current_results_df = current_results_df.sort_values(
        ["mean_test_score", "std_test_score"], ascending=[False, True]
    ).reset_index(drop=True)

    config = {
        "run_tag": run_tag,
        "append_existing": args.append_existing,
        "demographics_only": args.demographics_only,
        "condition": args.condition,
        "response_var": args.response_var,
        "eval_metric": args.eval_metric,
        "num_states": args.num_states,
        "n_jobs": args.n_jobs,
        "corr_threshold": args.corr_threshold,
        "models": list(selected_models.keys()),
        "combos": combo_map,
    }

    results_csv = output_dir / "channel_sweep_results.csv"
    combo_csv = output_dir / "channel_sweep_best_by_combo.csv"
    pivot_csv = output_dir / "channel_sweep_score_pivot.csv"
    config_json = output_dir / "channel_sweep_config.json"
    summary_md = output_dir / "channel_sweep_summary.md"

    results_df = current_results_df
    if args.append_existing:
        existing_df = load_existing_results(
            results_csv,
            fallback_source_run=sanitize_name(output_dir.name),
        )
        if existing_df is not None:
            results_df = pd.concat([existing_df, current_results_df], ignore_index=True)
            results_df = results_df.sort_values(
                ["mean_test_score", "std_test_score"], ascending=[False, True]
            ).reset_index(drop=True)

    combo_best_df, pivot_df = build_aggregate_tables(results_df)

    results_df.to_csv(results_csv, index=False)
    combo_best_df.to_csv(combo_csv, index=False)
    pivot_df.to_csv(pivot_csv)
    config_json.write_text(json.dumps(config, indent=2), encoding="utf-8")
    write_markdown_summary(results_df, combo_best_df, summary_md)

    print("\nSaved:")
    print(results_csv)
    print(combo_csv)
    print(pivot_csv)
    print(config_json)
    print(summary_md)

    print("\nTop combos:")
    print(
        combo_best_df[
            [
                col
                for col in [
                    "source_run",
                    "combo_name",
                    "model_name",
                    "mean_test_score",
                    "std_test_score",
                    "channels",
                ]
                if col in combo_best_df.columns
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()

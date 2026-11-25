"""Z3003 Mini-Project Starter Pipeline: End-to-End Data Mining on Zanzibar Crop Data."""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.tree import DecisionTreeClassifier

ATTRIBUTE_SCHEMA = {
    "farm_id": "ID (unique farm identifier)",
    "region": "nominal (5 Zanzibar administrative regions)",
    "crop": "nominal (Clove, Cashew, Rice, Coconut, Cassava)",
    "farm_size_ha": "numeric (cultivated area in hectares)",
    "yield_tonnes": "numeric (seasonal crop yield in tonnes)",
    "rainfall_mm": "numeric (seasonal rainfall in millimeters)",
    "price_per_kg": "numeric (farm-gate price in USD/kg)",
    "fertilizer_used": "binary (Yes / No input indicator)",
    "revenue_usd": "numeric (gross farm revenue in USD)",
}


def load_or_generate_dataset(csv_path: Path | None = None) -> pd.DataFrame:
    """Load W1_zanzibar_crop_sample.csv if available, else synthesize a schema-matched fallback for Colab."""
    if csv_path is None:
        candidate = Path(__file__).resolve().parent.parent / "resources" / "W1_zanzibar_crop_sample.csv"
        if candidate.exists():
            csv_path = candidate
    if csv_path is not None and csv_path.exists():
        return pd.read_csv(csv_path)

    rng = random.Random(3003)
    crops = [("Clove", 7.5, 1.8), ("Cashew", 2.0, 1.4), ("Rice", 0.7, 2.5), ("Coconut", 0.4, 2.2), ("Cassava", 0.3, 3.0)]
    regions = ["Pemba North", "Pemba South", "North Unguja", "South Unguja", "Zanzibar Urban"]
    rows = []
    for fid in range(1, 501):
        crop, base_p, base_y = rng.choice(crops)
        size = round(rng.uniform(0.2, 4.5), 2)
        rain = round(rng.gauss(1350.0, 180.0), 1)
        fert = "Yes" if rng.random() < 0.6 else "No"
        yld = None if rng.random() < 0.048 else round(max(0.3, base_y + (0.25 if fert == "Yes" else 0.0) + rng.gauss(0, 0.35)), 2)
        price = round(max(0.2, base_p * rng.uniform(0.85, 1.15)), 2)
        rev = round((yld if yld is not None else base_y) * 1000.0 * price, 2)
        rows.append(
            {
                "farm_id": fid,
                "region": rng.choice(regions),
                "crop": crop,
                "farm_size_ha": size,
                "yield_tonnes": yld,
                "rainfall_mm": rain,
                "price_per_kg": price,
                "fertilizer_used": fert,
                "revenue_usd": rev,
            }
        )
    return pd.DataFrame(rows)


def audit_data_understanding(df: pd.DataFrame) -> dict[str, object]:
    """Section 1: Verify shape, attribute types, and missing-value counts."""
    missing = {col: int(df[col].isna().sum()) for col in df.columns if df[col].isna().sum() > 0}
    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "schema": ATTRIBUTE_SCHEMA,
        "missing_counts": missing,
    }


def exploratory_analysis(df: pd.DataFrame) -> dict[str, object]:
    """Section 2: Summary stats, price-revenue confounder check, and Euclidean distance on z-scores."""
    corr = float(df["price_per_kg"].corr(df["revenue_usd"]))
    crop_means = df.groupby("crop")[["price_per_kg", "revenue_usd"]].mean().round(2).to_dict(orient="index")
    num_cols = ["farm_size_ha", "rainfall_mm", "price_per_kg"]
    mat = df[num_cols].fillna(df[num_cols].median()).to_numpy(dtype=float)
    mu = mat.mean(axis=0)
    sd = np.where(mat.std(axis=0) == 0, 1.0, mat.std(axis=0))
    z = (mat - mu) / sd
    dist_0_1 = float(np.linalg.norm(z[0] - z[1]))
    return {
        "price_revenue_corr": round(corr, 4),
        "crop_confounder_means": crop_means,
        "sample_z_euclidean_dist": round(dist_0_1, 4),
    }


def run_leakage_free_benchmark(df: pd.DataFrame, seed: int = 3003) -> dict[str, object]:
    """Sections 3 & 4: Leakage-free preprocessing, classification benchmark, and KMeans silhouette sweep."""
    # Target: predict whether farm revenue exceeds dataset median (binary high/low revenue)
    clean_df = df.dropna(subset=["revenue_usd"]).copy()
    med_rev = float(clean_df["revenue_usd"].median())
    clean_df["high_revenue"] = (clean_df["revenue_usd"] >= med_rev).astype(int)

    feature_cols = ["region", "crop", "farm_size_ha", "yield_tonnes", "rainfall_mm", "fertilizer_used"]
    X = clean_df[feature_cols]
    y = clean_df["high_revenue"].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=seed, stratify=y
    )

    num_features = ["farm_size_ha", "yield_tonnes", "rainfall_mm"]
    cat_features = ["region", "crop", "fertilizer_used"]

    prep = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", RobustScaler())]),
                num_features,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="most_frequent")),
                        ("ohe", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                cat_features,
            ),
        ]
    )

    models = {
        "logistic": LogisticRegression(max_iter=500, random_state=seed),
        "decision_tree": DecisionTreeClassifier(max_depth=5, random_state=seed),
        "random_forest": RandomForestClassifier(n_estimators=80, max_depth=6, random_state=seed),
    }
    clf_results: dict[str, dict[str, object]] = {}
    for name, clf in models.items():
        pipe = Pipeline([("prep", prep), ("clf", clf)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        clf_results[name] = {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "f1": round(float(f1_score(y_test, preds)), 4),
            "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        }

    # Unsupervised clustering on train-fitted numeric features (k=2..5)
    X_num = prep.fit_transform(X_train)
    if hasattr(X_num, "toarray"):
        X_num = X_num.toarray()
    sil_scores: dict[int, float] = {}
    for k in range(2, 6):
        km = KMeans(n_clusters=k, n_init=10, random_state=seed)
        labels = km.fit_predict(X_num)
        sil_scores[k] = round(float(silhouette_score(X_num, labels)), 4)
    best_k = max(sil_scores, key=lambda kk: sil_scores[kk])

    return {
        "median_revenue_usd": round(med_rev, 2),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "classifiers": clf_results,
        "clustering_silhouette": sil_scores,
        "best_k": int(best_k),
    }


def export_reproducible_artifacts(
    audit: dict[str, object],
    eda: dict[str, object],
    bench: dict[str, object],
    out_dir: Path,
) -> tuple[Path, Path]:
    """Section 5: Export JSON metrics and plain-language summary report."""
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "mini_project_metrics.json"
    md_path = out_dir / "mini_project_summary.md"

    payload = {"data_understanding": audit, "eda": eda, "benchmark": bench}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    rf_acc = bench["classifiers"]["random_forest"]["accuracy"]
    summary_md = (
        "# Z3003 Mini-Project Findings Summary\n\n"
        f"- Dataset shape: {audit['rows']} farms x {audit['cols']} attributes; "
        f"missing counts: {audit['missing_counts']}.\n"
        f"- Confounder finding: farm-gate price and revenue correlate strongly (r = {eda['price_revenue_corr']}) "
        "because crop type (especially cloves) drives both price per kg and revenue.\n"
        f"- Mining benchmark: leakage-free Random Forest achieved held-out accuracy {rf_acc:.3f}; "
        f"KMeans selected k = {bench['best_k']} by silhouette score.\n"
        "- Scaling (1,000x larger, ~500,000 rows): apply stratified sampling by region before clustering "
        "and swap exact PCA for randomized/incremental PCA.\n"
        "- Ethics note: avoid publishing unmasked farm coordinates or using yield predictions to deny "
        "smallholder cooperative credit without field verification.\n"
    )
    md_path.write_text(summary_md, encoding="utf-8")
    return json_path, md_path


def run_tests() -> None:
    df = load_or_generate_dataset()
    audit = audit_data_understanding(df)
    assert audit["rows"] >= 300 and audit["cols"] >= 5
    eda = exploratory_analysis(df)
    assert eda["price_revenue_corr"] > 0.5
    bench = run_leakage_free_benchmark(df)
    assert bench["classifiers"]["random_forest"]["accuracy"] >= 0.75
    assert bench["best_k"] in {2, 3, 4, 5}
    with tempfile.TemporaryDirectory() as tmp:
        jp, mp = export_reproducible_artifacts(audit, eda, bench, Path(tmp))
        assert jp.exists() and mp.exists()
        parsed = json.loads(jp.read_text(encoding="utf-8"))
        assert parsed["benchmark"]["best_k"] == bench["best_k"]
    print(
        f"MP01 starter tests passed ({audit['rows']} rows, r={eda['price_revenue_corr']}, "
        f"RF acc={bench['classifiers']['random_forest']['accuracy']}, best_k={bench['best_k']})."
    )


if __name__ == "__main__":
    run_tests()

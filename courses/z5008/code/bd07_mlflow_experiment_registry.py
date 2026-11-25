"""Z5008 Lab Module 07: Local MLflow-Style Experiment Tracking and Model Registry Gates."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path


class LocalModelRegistry:
    """SQLite-backed experiment tracker and staged model registry (Staging -> Production -> Archived)."""

    VALID_STAGES = {"None", "Staging", "Production", "Archived"}

    def __init__(self, db_path: Path) -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Runs (
                run_id TEXT PRIMARY KEY,
                experiment TEXT NOT NULL,
                params_json TEXT NOT NULL,
                metrics_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ModelVersions (
                model_name TEXT NOT NULL,
                version INTEGER NOT NULL,
                run_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                PRIMARY KEY (model_name, version)
            );
            """
        )

    def log_run(self, run_id: str, experiment: str, params: dict, metrics: dict) -> None:
        self.conn.execute(
            "INSERT INTO Runs VALUES (?, ?, ?, ?)",
            (run_id, experiment, json.dumps(params), json.dumps(metrics)),
        )
        self.conn.commit()

    def register_model(self, model_name: str, run_id: str) -> int:
        row = self.conn.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 FROM ModelVersions WHERE model_name = ?",
            (model_name,),
        ).fetchone()
        version = int(row[0])
        self.conn.execute(
            "INSERT INTO ModelVersions VALUES (?, ?, ?, 'None')",
            (model_name, version, run_id),
        )
        self.conn.commit()
        return version

    def transition_stage(self, model_name: str, version: int, new_stage: str, min_f1: float = 0.80) -> None:
        if new_stage not in self.VALID_STAGES:
            raise ValueError(f"Unsupported stage: {new_stage}")
        if new_stage == "Production":
            row = self.conn.execute(
                """
                SELECT r.metrics_json FROM ModelVersions m
                JOIN Runs r ON m.run_id = r.run_id
                WHERE m.model_name = ? AND m.version = ?
                """,
                (model_name, version),
            ).fetchone()
            assert row is not None, "Unknown model version"
            metrics = json.loads(row[0])
            if metrics.get("f1", 0.0) < min_f1:
                raise ValueError(f"Gate blocked promotion: f1={metrics.get('f1')} < {min_f1}")
            # Archive any existing Production version before promoting the new champion
            self.conn.execute(
                "UPDATE ModelVersions SET stage = 'Archived' WHERE model_name = ? AND stage = 'Production'",
                (model_name,),
            )
        self.conn.execute(
            "UPDATE ModelVersions SET stage = ? WHERE model_name = ? AND version = ?",
            (new_stage, model_name, version),
        )
        self.conn.commit()

    def best_run(self, experiment: str, metric_key: str) -> tuple[str, float]:
        rows = self.conn.execute("SELECT run_id, metrics_json FROM Runs WHERE experiment = ?", (experiment,)).fetchall()
        scored = [(rid, float(json.loads(mj)[metric_key])) for rid, mj in rows]
        return max(scored, key=lambda x: x[1])

    def close(self) -> None:
        self.conn.close()


def run_tests() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = LocalModelRegistry(Path(tmp) / "mlflow_local.db")
        reg.log_run("run_01", "zanzibar_churn", {"max_depth": 4, "n_estimators": 50}, {"f1": 0.77, "auc": 0.82})
        reg.log_run("run_02", "zanzibar_churn", {"max_depth": 8, "n_estimators": 150}, {"f1": 0.89, "auc": 0.94})
        v1 = reg.register_model("churn_gbdt", "run_01")
        v2 = reg.register_model("churn_gbdt", "run_02")

        # Promote v1 to Staging, verify Production gate blocks v1 (f1=0.77 < 0.80)
        reg.transition_stage("churn_gbdt", v1, "Staging")
        try:
            reg.transition_stage("churn_gbdt", v1, "Production", min_f1=0.80)
            raise AssertionError("Gate should have rejected v1")
        except ValueError:
            pass

        # Promote v2 to Production
        reg.transition_stage("churn_gbdt", v2, "Production", min_f1=0.80)
        best_id, best_f1 = reg.best_run("zanzibar_churn", "f1")
        assert best_id == "run_02" and best_f1 == 0.89
        stages = dict(
            reg.conn.execute("SELECT version, stage FROM ModelVersions WHERE model_name = 'churn_gbdt'").fetchall()
        )
        assert stages == {1: "Staging", 2: "Production"}
        reg.close()
    print("BD07 self-tests passed (Run logging, best-run selection, and Production promotion gate verified).")


if __name__ == "__main__":
    run_tests()

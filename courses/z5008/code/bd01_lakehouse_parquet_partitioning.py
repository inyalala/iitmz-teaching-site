"""Z5008 Lab Module 01: Lakehouse Medallion Partitioning, Delta ACID Versioning, and Time Travel."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
import tempfile
from typing import Any


@dataclass(frozen=True)
class TxRecord:
    tx_id: str
    region: str
    category: str
    amount_usd: float
    date: str


class MiniDeltaTable:
    """Pedagogical ACID Lakehouse table implementing append/upsert commits and version time travel."""

    def __init__(self, root: Path, partition_by: str = "region") -> None:
        self.root = root
        self.partition_by = partition_by
        self.log_dir = root / "_delta_log"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.version = -1

    def commit(self, records: list[dict[str, Any]], mode: str = "append") -> int:
        prev_rows: dict[str, dict[str, Any]] = {}
        if mode == "merge" and self.version >= 0:
            for r in self.read(version=self.version):
                prev_rows[str(r["tx_id"])] = r
        elif mode == "append" and self.version >= 0:
            for r in self.read(version=self.version):
                prev_rows[str(r["tx_id"])] = r

        for r in records:
            prev_rows[str(r["tx_id"])] = r

        self.version += 1
        part_files: list[str] = []
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in prev_rows.values():
            pkey = str(row[self.partition_by])
            grouped.setdefault(pkey, []).append(row)

        for pval, rows in sorted(grouped.items()):
            pdir = self.root / f"{self.partition_by}={pval}"
            pdir.mkdir(parents=True, exist_ok=True)
            fname = f"part-v{self.version:04d}.json"
            (pdir / fname).write_text(json.dumps(rows, indent=2), encoding="utf-8")
            part_files.append(f"{self.partition_by}={pval}/{fname}")

        commit_meta = {"version": self.version, "mode": mode, "files": part_files, "row_count": len(prev_rows)}
        (self.log_dir / f"{self.version:020d}.json").write_text(json.dumps(commit_meta, indent=2), encoding="utf-8")
        return self.version

    def read(self, version: int | None = None, partition_filter: str | None = None) -> tuple[list[dict[str, Any]], int]:
        v = self.version if version is None else version
        meta = json.loads((self.log_dir / f"{v:020d}.json").read_text(encoding="utf-8"))
        rows: list[dict[str, Any]] = []
        files_scanned = 0
        for rel in meta["files"]:
            if partition_filter and not rel.startswith(f"{self.partition_by}={partition_filter}/"):
                continue
            files_scanned += 1
            rows.extend(json.loads((self.root / rel).read_text(encoding="utf-8")))
        return rows, files_scanned

    def read(self, version: int | None = None) -> list[dict[str, Any]]:  # type: ignore[misc]
        rows, _ = self.read_with_stats(version=version)
        return rows

    def read_with_stats(self, version: int | None = None, partition_filter: str | None = None) -> tuple[list[dict[str, Any]], int]:
        v = self.version if version is None else version
        meta = json.loads((self.log_dir / f"{v:020d}.json").read_text(encoding="utf-8"))
        rows: list[dict[str, Any]] = []
        scanned = 0
        for rel in meta["files"]:
            if partition_filter and not rel.startswith(f"{self.partition_by}={partition_filter}/"):
                continue
            scanned += 1
            rows.extend(json.loads((self.root / rel).read_text(encoding="utf-8")))
        return rows, scanned


def run_tests() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tbl = MiniDeltaTable(Path(tmp), partition_by="region")
        v0 = tbl.commit(
            [
                asdict(TxRecord("T1", "Zanzibar", "Agro", 120.0, "2026-05-01")),
                asdict(TxRecord("T2", "Dar", "Tech", 310.0, "2026-05-01")),
            ]
        )
        v1 = tbl.commit(
            [
                asdict(TxRecord("T2", "Dar", "Tech", 355.0, "2026-05-02")),  # UPSERT
                asdict(TxRecord("T3", "Nairobi", "Agro", 90.0, "2026-05-02")),
            ],
            mode="merge",
        )
        assert v0 == 0 and v1 == 1
        old_rows = tbl.read(version=0)
        new_rows, scanned = tbl.read_with_stats(version=1, partition_filter="Dar")
        assert len(old_rows) == 2 and len(new_rows) == 1 and new_rows[0]["amount_usd"] == 355.0 and scanned == 1
    print("BD01 self-tests passed (Partition pruning, MERGE upsert, and Delta time travel).")


if __name__ == "__main__":
    run_tests()

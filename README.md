# IIT Madras Zanzibar Teaching Materials Archive

Public course materials portal for Dr. Innocent Nyalala (Assistant Professor of Data Science and Artificial Intelligence, Indian Institute of Technology Madras Zanzibar), hosted at:
`https://inyalala.github.io/iitmz-teaching-site/`

Linked directly from the faculty portfolio at `https://inyalala.github.io/courses/`.

## Courses Hosted

| Code | Title | Programme | Term | Interactive Practice & Code |
| :--- | :--- | :--- | :--- | :--- |
| `Z5007` | Programming and Data Structures | MTech DSAI Core | Odd 2026-27 | 17 Weekly Code Modules, Project Benchmark, Question Bank, End-Sem Mock |
| `Z3003` | Data Mining: Scaling to Large Data | BS Core (with Dr. Mahendran V) | Odd 2026-27 | 26 Slide Decks, 10 Python/Colab Labs, Lab Explorer, Question Bank |
| `Z2005` | Programming and Data Structures | BS Reference | Odd Reference | Shared Z5007 Parity Roadmap, Notebooks, and Summaries |
| `Z2004` | Database Management Systems | BS Core | Even 2026 Archive | Lectures L01-L45, 8 SQLite/Python Labs, Lab Explorer, 66-Q Bank |
| `Z5008` | Big Data Lab | MTech DSAI Lab | Even 2026 Archive | 15 Lab Slides, 7 Spark/Lakehouse/MLflow Labs, Lab Explorer, 68-Q Bank |

## Local Preview & Automated Verification

1. Install Python dependencies (`Python 3.9+`):
   ```bash
   pip install -r requirements.txt
   ```
2. Run all four automated course self-test suites:
   ```bash
   python -m unittest courses/z5007/tests/test_z5007_all.py courses/dm-scale/tests/test_z3003_all.py courses/z2004/tests/test_z2004_all.py courses/z5008/tests/test_z5008_all.py -v
   ```
3. Preview the static site locally:
   ```bash
   python -m http.server 8000
   ```

## Updating Slides & Semester Archiving

See [`docs/TEACHING_WORKFLOW.md`](docs/TEACHING_WORKFLOW.md) and `scripts/add_lecture.py`.

## Licensing

All lecture slides, notes, lab sheets, tutorials, notebooks, code modules, and question banks are licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (`CC BY-NC-SA 4.0`; see `LICENSE`).

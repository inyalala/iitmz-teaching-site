# Teaching Materials Workflow (25-Year Maintenance Guide)

This repository serves course pages, HTML Reveal.js slide decks, PDFs, PPTX decks, Jupyter/Colab notebooks, tutorials, and question banks at:
`https://inyalala.github.io/iitmz-teaching-site/`

The personal faculty gateway (`https://inyalala.github.io/courses/`) links directly to every course and session file hosted here.

## Course Directory Map

- `courses/z5007/`: Programming and Data Structures (MTech Core, Active Odd Semester 2026-27, Mon/Wed/Thu/Fri)
- `courses/dm-scale/`: Data Mining: Scaling to Large Data (`Z3003`, BS Core, Active Odd Semester 2026-27, co-taught with Dr. Mahendran V)
- `courses/z2005/`: Programming and Data Structures (BS Reference Archive, Odd Semester)
- `courses/z2004/`: Database Management Systems (BS Core, Even Semester Archive)
- `courses/z5008/`: Big Data Lab (MTech Core Lab, Even Semester Archive)

## 1. Updating or Uploading Lecture Slides

For any recurring lecture or lab slide update, overwrite the existing canonical filename so student bookmarks, Google Classroom links, and `inyalala.github.io` links stay valid without manual path edits, or use the helper script for new files:

```bash
python scripts/add_lecture.py \
  --course z5007 \
  --file "C:/Users/Prof/Downloads/lecture-4.pdf" \
  --subdir 07-sorting
```

## 2. Archiving Semesters Without Copying Folders

Keep course paths permanent across years (`courses/z5007/`). At the end of each semester, create an immutable Git tag recording that exact term offering (Git tags snapshot the entire repository tree, so you can tag per course or once per semester across all courses):

```bash
git tag -a 2026-odd -m "Archive Odd Semester 2026-27 (Z5007, Z3003)"
git push origin 2026-odd
```

## 3. Large Files (> 40 MB) & Private Assessments

- Keep videos, raw datasets, and large container images in **GitHub Releases** on `inyalala/iitmz-teaching-site` (up to 2 GB per file) and link their Release URLs rather than committing large binaries into Git history.
- Keep exams, grading rubrics, and solution keys inside `iitmz-teaching-private`, separate from this public repository.

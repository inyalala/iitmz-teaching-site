-- Z2004 Relational Schema & Sample Data (SQLite / Standard SQL)
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Enrolment;
DROP TABLE IF EXISTS Course;
DROP TABLE IF EXISTS Student;

CREATE TABLE Student (
    SID        INTEGER PRIMARY KEY AUTOINCREMENT,
    Name       TEXT    NOT NULL,
    Dept       TEXT    NOT NULL,
    GPA        REAL    CHECK (GPA IS NULL OR (GPA BETWEEN 0.00 AND 4.00)),
    Email      TEXT    UNIQUE
);

CREATE TABLE Course (
    CID     TEXT    PRIMARY KEY,
    CName   TEXT    NOT NULL,
    Credits INTEGER NOT NULL DEFAULT 3 CHECK (Credits IN (1, 2, 3, 4))
);

CREATE TABLE Enrolment (
    SID   INTEGER NOT NULL,
    CID   TEXT    NOT NULL,
    Grade TEXT    CHECK (Grade IN ('A', 'B', 'C', 'D', 'F') OR Grade IS NULL),
    PRIMARY KEY (SID, CID),
    FOREIGN KEY (SID) REFERENCES Student(SID) ON DELETE CASCADE,
    FOREIGN KEY (CID) REFERENCES Course(CID) ON DELETE CASCADE
);

INSERT INTO Student (Name, Dept, GPA, Email) VALUES
    ('Asha Ali', 'CSE', 3.80, 'asha.ali@iitmz.example'),
    ('Omar Said', 'CSE', 3.20, 'omar.said@iitmz.example'),
    ('Zahra Musa', 'EEE', NULL, 'zahra.musa@iitmz.example'),
    ('Noah Kim', 'CSE', 3.92, 'noah.kim@iitmz.example'),
    ('Fatima Noor', 'CE', 3.28, 'fatima.noor@iitmz.example');

INSERT INTO Course (CID, CName, Credits) VALUES
    ('DB101', 'Database Management Systems', 3),
    ('CS102', 'Programming and Data Structures', 4),
    ('EE105', 'Circuits I', 3);

INSERT INTO Enrolment (SID, CID, Grade) VALUES
    (1, 'DB101', 'A'),
    (1, 'CS102', 'A'),
    (2, 'DB101', 'B'),
    (3, 'EE105', 'C'),
    (4, 'DB101', 'A'),
    (4, 'CS102', 'B');

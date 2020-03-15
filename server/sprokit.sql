CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jobNumber CHAR(48) NOT NULL,
    userID CHAR(48) NOT NULL,
    Q100_response TEXT,
    Q101_response TEXT,
    Q102_response TEXT,
    Q104_response TEXT,
    Q201_response TEXT,
    Q300_response TEXT,
    Q301_response TEXT,
    Q303_response TEXT,
    Q304_response TEXT,
    Q402_response TEXT,
    Q403_response TEXT,
    status CHAR(32),
    createdAt DATETIME DEFAULT current_timestamp
);

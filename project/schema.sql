-- Create table for users
CREATE TABLE "users" (
    "id" INTEGER,
    "username" TEXT NOT NULL,
    "hash" TEXT NOT NULL,
    PRIMARY KEY("id")
);

CREATE INDEX "user_search" ON "users" ("id", "username");

-- Create table for each Chinese Class
CREATE TABLE "classes" (
    "id" INTEGER,
    "date" TEXT NOT NULL,
    PRIMARY KEY("id")
);

-- Create table including all vocab words to be included in the project
CREATE TABLE "vocab" (
    "id" INTEGER,
    "class_id" INTEGER,
    "chinese" TEXT NOT NULL,
    "pinyin" TEXT NOT NULL,
    "toneless" TEXT NOT NULL,
    "english" TEXT NOT NULL,
    "length" INTEGER NOT NULL,
    "source" INTEGER NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("class_id") REFERENCES "classes"("id")
);

CREATE INDEX "vocab_search" ON "vocab" ("id", "chinese", "pinyin", "english", "length");

-- Create table to keep track of quiz scores
CREATE TABLE "quizzes" (
    "id" INTEGER,
    "user_id" INTEGER NOT NULL,
    "type" TEXT NOT NULL,
    "questions" INTEGER NOT NULL,
    "correct" INTEGER NOT NULL,
    "score" REAL NOT NULL,
    "datetime" NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id"),
    FOREIGN KEY("user_id") REFERENCES "users"("id")
);

-- Create table to keep track of accuracy in answering questions on each vocab word/phrase
CREATE TABLE "accuracy" (
    "id" INTEGER,
    "user_id" INTEGER NOT NULL,
    "vocab_id" INTEGER NOT NULL UNIQUE,
    "seen" INTEGER NOT NULL,
    "correct" INTEGER NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("user_id") REFERENCES "users"("id")
    FOREIGN KEY("vocab_id") REFERENCES "vocab"("id")
);

-- Create a view for average quiz scores
CREATE VIEW "average scores" AS
SELECT user_id, AVG("score") AS 'average score' FROM quizzes
GROUP BY user_id
ORDER BY AVG("score") DESC

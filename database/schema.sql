CREATE DATABASE nodue;

\c nodue;

CREATE TABLE students(
id SERIAL PRIMARY KEY,
name VARCHAR(100),
reg_no VARCHAR(50),
department VARCHAR(100),
semester VARCHAR(10),
password VARCHAR(100)
);

CREATE TABLE faculty(
id SERIAL PRIMARY KEY,
name VARCHAR(100),
username VARCHAR(50),
password VARCHAR(100)
);

CREATE TABLE hod(
id SERIAL PRIMARY KEY,
name VARCHAR(100),
username VARCHAR(50),
password VARCHAR(100)
);

CREATE TABLE applications(
id SERIAL PRIMARY KEY,
reg_no VARCHAR(50),
subject_code VARCHAR(20),
subject_name VARCHAR(100),
faculty_name VARCHAR(100),
faculty_status VARCHAR(20) DEFAULT 'Pending',
hod_status VARCHAR(20) DEFAULT 'Pending'
);
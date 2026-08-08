-- Run this once to create the database and table.
-- (Flask-SQLAlchemy will also auto-create the table on first run via db.create_all(),
--  but this file documents the schema explicitly as required by the assignment.)

CREATE DATABASE IF NOT EXISTS users
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE users;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users (email);

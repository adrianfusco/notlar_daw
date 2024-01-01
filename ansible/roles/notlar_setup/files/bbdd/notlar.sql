DO $$ 
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'notlar') THEN
    CREATE DATABASE notlar;
  END IF;
END $$;

\c notlar;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name VARCHAR(80),
    last_name VARCHAR(80),
    phone_number VARCHAR(20),
    telegram_user VARCHAR(80),
    profile_picture VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    color VARCHAR(7) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

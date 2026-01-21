CREATE TABLE mice (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    genetic_line VARCHAR(100) NOT NULL,
    sex VARCHAR(10) NOT NULL,
    age_weeks INTEGER NOT NULL,
    device_id INTEGER references devices(id),
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE devices(
    id SERIAL PRIMARY KEY,
    device_name VARCHAR(50)
);
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(15) NOT NULL,
    password VARCHAR(15) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE experiments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    description TEXT,
    date TIMESTAMP DEFAULT NOW()
);
CREATE TABLE mice_experiments (
    mouse_id INTEGER REFERENCES mice(id),
    experiment_id INTEGER REFERENCES experiments(id),
    PRIMARY KEY (mouse_id, experiment_id)
);
CREATE TABLE structures (
    id SERIAL PRIMARY KEY,
    mouse_id INTEGER REFERENCES mice(id),
    meninges BOOLEAN DEFAULT FALSE,
    brain BOOLEAN DEFAULT FALSE
);
CREATE TABLE structures_meninges (
    id SERIAL PRIMARY KEY,
    structures_id INTEGER REFERENCES structures(id),
    superior_sagittal_sinus BOOLEAN DEFAULT FALSE,
    confluence_of_sinuses BOOLEAN DEFAULT FALSE,
    transverse_sinus BOOLEAN DEFAULT FALSE
);
CREATE TABLE structures_brain (
    id SERIAL PRIMARY KEY,
    structures_id INTEGER REFERENCES structures(id),
    cortex BOOLEAN DEFAULT FALSE,
    thalamus BOOLEAN DEFAULT FALSE,
    hypothalamus BOOLEAN DEFAULT FALSE
);
CREATE TABLE ihc (
    id SERIAL PRIMARY KEY,
    structures_brain_id INTEGER REFERENCES structures_brain(id),
    dapi BOOLEAN DEFAULT FALSE,
    sma BOOLEAN DEFAULT FALSE,
    lyve1 BOOLEAN DEFAULT FALSE,
    cd68 BOOLEAN DEFAULT FALSE
);
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    mouse_id INTEGER REFERENCES mice(id),
    experiment_id INTEGER REFERENCES experiments(id),
    structure_id INTEGER REFERENCES structures(id),
    ihc_id INTEGER REFERENCES ihc(id),
    s3_path TEXT NOT NULL,
    resolution VARCHAR(50),
    channels INTEGER,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
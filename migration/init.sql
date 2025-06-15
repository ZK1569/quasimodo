CREATE TABLE IF NOT EXISTS face (
    id SERIAL PRIMARY KEY,
    lastname VARCHAR(100) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    face_embeddings BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

create table histories (
	id SERIAL PRIMARY KEY,
	fullname VARCHAR(255),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO histories (fullname, created_at)
SELECT
    (ARRAY[
        'Alice Martin', 'Bob Dupont',  'Charlie Durand', 'Diane Petit',
        'Éric Bernard', 'Fanny Leroy', 'Gilles Moreau',  'Hélène Garcia',
        'Ivan Laurent', 'Julie Renault', 'Kevin Fontaine','Laura Roussel',
        'Marc Blanchard','Nina Faure',  'Oscar Roux',    'Pauline Vidal',
        'Quentin Henry','Rita Gauthier','Steve Colin',    'Tina Marchand'
    ])[1 + floor(random() * 20)::int] AS fullname,

    -- Créé une date-heure aléatoire entre 2025-06-01 00:00 et 2025-06-30 23:59
    timestamp '2025-06-01 00:00'
    + (floor(random() * 30)::int) * interval '1 day'
    + (floor(random() * 24)::int) * interval '1 hour'
    + (floor(random() * 60)::int) * interval '1 minute'
    + (floor(random() * 60)::int) * interval '1 second' AS created_at
FROM generate_series(1, 50);

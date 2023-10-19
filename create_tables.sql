CREATE TABLE user (
    id serial PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

INSERT INTO user (username, password) VALUES ('example_user', 'example_password');


CREATE TABLE trainers (
    trainer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),
    level INTEGER
);


CREATE TABLE pokemons (
    pokemon_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    type VARCHAR(50),
    level INTEGER,
    trainer_id INTEGER REFERENCES trainers(trainer_id)
);

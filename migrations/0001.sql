DROP TABLE IF EXISTS users_buildings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS buildings;
CREATE TABLE IF NOT EXISTS users
(
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    currency BIGINT DEFAULT 0
); 
CREATE TABLE IF NOT EXISTS buildings
(
    id SERIAL PRIMARY KEY,
    cost BIGINT UNIQUE NOT NULL,
    income BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS users_buildings
(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    building_id BIGINT NOT NULL,
    count BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (building_id) REFERENCES buildings(id),
    UNIQUE (user_id,building_id)
);

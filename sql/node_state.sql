CREATE TABLE IF NOT EXISTS node_state (
    time_stamp TIMESTAMP DEFAULT NOW(),
    node TEXT NOT NULL,
    light int NOT NULL,
    cpu_temp FLOAT NOT NULL,
    env_temp FLOAT NOT NULL
);

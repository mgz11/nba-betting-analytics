DROP TABLE IF EXISTS raw_odds_snapshots;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS team_game_features;

CREATE TABLE raw_odds_snapshots (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    fetch_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    snapshot_date DATE NOT NULL,
    raw_json JSONB NOT NULL
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    external_game_id TEXT UNIQUE,
    game_date DATE NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,

    home_score INTEGER,
    away_score INTEGER,

    spread_home NUMERIC,
    spread_away NUMERIC,
    moneyline_home INTEGER,
    moneyline_away INTEGER,
    total NUMERIC,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_game_features (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,

    team TEXT NOT NULL,
    opponent_team TEXT NOT NULL,
    is_home BOOLEAN NOT NULL,

    team_score INTEGER,
    opponent_score INTEGER, 
    point_diff INTEGER,

    rest_days INTEGER,
    recent_avg_margin NUMERIC,
    recent_win_pct NUMERIC,

    is_favorite BOOLEAN,
    spread NUMERIC,
    covered_spread BOOLEAN,
    spread_diff NUMERIC
);
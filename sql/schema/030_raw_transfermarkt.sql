-- Raw Transfermarkt tables: faithful copy of the 12 Kaggle CSVs (Version 679).
-- Every column is TEXT on purpose: typing and cleaning happen in the core schema.
-- Column order matches each CSV header; loaders use COPY ... (FORMAT csv, HEADER MATCH).

CREATE TABLE IF NOT EXISTS raw.tm_appearances (
    appearance_id text,
    game_id text,
    player_id text,
    player_club_id text,
    player_current_club_id text,
    date text,
    player_name text,
    competition_id text,
    yellow_cards text,
    red_cards text,
    goals text,
    assists text,
    minutes_played text
);

CREATE TABLE IF NOT EXISTS raw.tm_club_games (
    game_id text,
    club_id text,
    own_goals text,
    own_position text,
    own_manager_name text,
    opponent_id text,
    opponent_goals text,
    opponent_position text,
    opponent_manager_name text,
    hosting text,
    is_win text
);

CREATE TABLE IF NOT EXISTS raw.tm_clubs (
    club_id text,
    club_code text,
    name text,
    domestic_competition_id text,
    total_market_value text,
    squad_size text,
    average_age text,
    foreigners_number text,
    foreigners_percentage text,
    national_team_players text,
    stadium_name text,
    stadium_seats text,
    net_transfer_record text,
    coach_name text,
    last_season text,
    filename text,
    url text
);

CREATE TABLE IF NOT EXISTS raw.tm_competitions (
    competition_id text,
    competition_code text,
    name text,
    sub_type text,
    type text,
    country_id text,
    country_name text,
    domestic_league_code text,
    confederation text,
    total_clubs text,
    url text
);

CREATE TABLE IF NOT EXISTS raw.tm_countries (
    country_id text,
    country_name text,
    country_code text,
    confederation text,
    total_clubs text,
    total_players text,
    average_age text,
    url text
);

CREATE TABLE IF NOT EXISTS raw.tm_game_events (
    game_event_id text,
    date text,
    game_id text,
    minute text,
    type text,
    club_id text,
    club_name text,
    player_id text,
    description text,
    player_in_id text,
    player_assist_id text
);

CREATE TABLE IF NOT EXISTS raw.tm_game_lineups (
    game_lineups_id text,
    date text,
    game_id text,
    player_id text,
    club_id text,
    player_name text,
    type text,
    position text,
    number text,
    team_captain text
);

CREATE TABLE IF NOT EXISTS raw.tm_games (
    game_id text,
    competition_id text,
    season text,
    round text,
    date text,
    home_club_id text,
    away_club_id text,
    home_club_goals text,
    away_club_goals text,
    home_club_position text,
    away_club_position text,
    home_club_manager_name text,
    away_club_manager_name text,
    stadium text,
    attendance text,
    referee text,
    url text,
    home_club_formation text,
    away_club_formation text,
    home_club_name text,
    away_club_name text,
    aggregate text,
    competition_type text
);

CREATE TABLE IF NOT EXISTS raw.tm_national_teams (
    national_team_id text,
    name text,
    team_code text,
    country_id text,
    country_name text,
    country_code text,
    confederation text,
    team_image_url text,
    squad_size text,
    average_age text,
    foreigners_number text,
    foreigners_percentage text,
    total_market_value text,
    coach_name text,
    fifa_ranking text,
    last_season text,
    url text
);

CREATE TABLE IF NOT EXISTS raw.tm_player_valuations (
    player_id text,
    date text,
    market_value_in_eur text,
    current_club_name text,
    current_club_id text,
    player_club_domestic_competition_id text
);

CREATE TABLE IF NOT EXISTS raw.tm_players (
    player_id text,
    first_name text,
    last_name text,
    name text,
    last_season text,
    current_club_id text,
    player_code text,
    country_of_birth text,
    city_of_birth text,
    country_of_citizenship text,
    date_of_birth text,
    sub_position text,
    position text,
    foot text,
    height_in_cm text,
    contract_expiration_date text,
    agent_name text,
    image_url text,
    international_caps text,
    international_goals text,
    current_national_team_id text,
    url text,
    current_club_domestic_competition_id text,
    current_club_name text,
    market_value_in_eur text,
    highest_market_value_in_eur text
);

CREATE TABLE IF NOT EXISTS raw.tm_transfers (
    player_id text,
    transfer_date text,
    transfer_season text,
    from_club_id text,
    to_club_id text,
    from_club_name text,
    to_club_name text,
    transfer_fee text,
    market_value_in_eur text,
    player_name text
);

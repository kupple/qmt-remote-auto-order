CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 9b65683001b8

CREATE TABLE account (
    remark VARCHAR, 
    status INTEGER, 
    is_connected INTEGER, 
    is_main INTEGER, 
    mini_qmt_path VARCHAR, 
    client_id VARCHAR, 
    client_type INTEGER, 
    ths_path VARCHAR, 
    ths_client_id VARCHAR, 
    ths_pwd VARCHAR, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE backtest (
    id INTEGER NOT NULL, 
    name VARCHAR, 
    order_count_type INTEGER, 
    service_charge NUMERIC, 
    accruing_amounts NUMERIC, 
    initial_capital NUMERIC, 
    lower_limit_of_fees NUMERIC, 
    final_amount NUMERIC, 
    task_id INTEGER, 
    frequency VARCHAR, 
    state VARCHAR, 
    can_use_amount NUMERIC, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE data_all_stocks (
    id INTEGER NOT NULL, 
    code VARCHAR, 
    name VARCHAR, 
    latest_price NUMERIC, 
    change_rate NUMERIC, 
    change_amount NUMERIC, 
    volume NUMERIC, 
    turnover NUMERIC, 
    amplitude NUMERIC, 
    highest NUMERIC, 
    lowest NUMERIC, 
    open NUMERIC, 
    close NUMERIC, 
    volume_ratio NUMERIC, 
    turnover_ratio NUMERIC, 
    pe_dynamic NUMERIC, 
    pb NUMERIC, 
    total_market_value NUMERIC, 
    circulating_market_value NUMERIC, 
    rise_speed NUMERIC, 
    five_minute_change NUMERIC, 
    sixty_days_change NUMERIC, 
    year_to_date_change NUMERIC, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE data_st_stocks (
    id INTEGER NOT NULL, 
    code VARCHAR, 
    name VARCHAR, 
    latest_price NUMERIC, 
    change_rate NUMERIC, 
    change_amount NUMERIC, 
    volume NUMERIC, 
    turnover NUMERIC, 
    amplitude NUMERIC, 
    highest NUMERIC, 
    lowest NUMERIC, 
    open NUMERIC, 
    close NUMERIC, 
    volume_ratio NUMERIC, 
    turnover_ratio NUMERIC, 
    pe_dynamic NUMERIC, 
    pb NUMERIC, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE data_table_record (
    table_name VARCHAR, 
    record_type INTEGER, 
    record_time VARCHAR, 
    record_content VARCHAR, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE data_trade_date_hist (
    id INTEGER NOT NULL, 
    trade_date VARCHAR, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE entrusts (
    traded_amount NUMERIC, 
    traded_price NUMERIC, 
    stock_code VARCHAR, 
    traded_volume NUMERIC, 
    traded_time INTEGER, 
    traded_id VARCHAR, 
    status_msg VARCHAR, 
    orders_id INTEGER, 
    order_type INTEGER, 
    price_type INTEGER, 
    order_id INTEGER, 
    order_status INTEGER, 
    order_sysid VARCHAR, 
    status INTEGER DEFAULT '0', 
    offset_flag INTEGER, 
    backtest_id INTEGER, 
    is_mock INTEGER DEFAULT '0', 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE INDEX ix_entrusts_is_mock ON entrusts (is_mock);

CREATE TABLE logger (
    id INTEGER NOT NULL, 
    timestamp VARCHAR, 
    logger_name VARCHAR, 
    level VARCHAR, 
    message VARCHAR, 
    module VARCHAR, 
    func_name VARCHAR, 
    line_num INTEGER, 
    exception VARCHAR, 
    user_id VARCHAR, 
    task_id INTEGER, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE orders (
    security_code VARCHAR, 
    fix_result_order_id VARCHAR, 
    style VARCHAR, 
    run_params VARCHAR, 
    pindex VARCHAR, 
    platform VARCHAR, 
    task_id INTEGER, 
    is_buy INTEGER DEFAULT '0', 
    strategy_code VARCHAR, 
    add_time VARCHAR, 
    volume INTEGER, 
    price NUMERIC, 
    avg_cost NUMERIC, 
    status_msg VARCHAR, 
    commission NUMERIC, 
    status INTEGER DEFAULT '0', 
    transaction_status INTEGER DEFAULT '0', 
    backtest_id INTEGER, 
    positions VARCHAR, 
    is_mock INTEGER DEFAULT '0', 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE INDEX ix_orders_is_mock ON orders (is_mock);

CREATE TABLE positions (
    security_code VARCHAR, 
    volume INTEGER, 
    amount NUMERIC, 
    task_id INTEGER, 
    average_price NUMERIC, 
    backtest_id INTEGER, 
    delete_time DATETIME, 
    is_mock INTEGER DEFAULT '0', 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE INDEX ix_positions_is_mock ON positions (is_mock);

CREATE TABLE ppx_storage_var (
    "key" VARCHAR NOT NULL, 
    val VARCHAR DEFAULT '' NOT NULL, 
    remark VARCHAR DEFAULT '' NOT NULL, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE INDEX ix_ppx_storage_var_key ON ppx_storage_var ("key");

CREATE TABLE setting (
    python_path VARCHAR, 
    mini_qmt_path VARCHAR, 
    client_id VARCHAR, 
    salt VARCHAR, 
    server_url VARCHAR, 
    run_model_type INTEGER DEFAULT '0', 
    auto_national_debt INTEGER DEFAULT '0', 
    auto_buy_stock_ipo INTEGER DEFAULT '0', 
    auto_buy_purchase_ipo INTEGER DEFAULT '0', 
    auto_reorder INTEGER DEFAULT '0', 
    auto_startup INTEGER DEFAULT '0', 
    account VARCHAR, 
    client_type INTEGER DEFAULT '1', 
    ths_path VARCHAR, 
    ths_pwd VARCHAR, 
    ths_client_id VARCHAR, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE tasklist (
    task_type INTEGER DEFAULT '1', 
    name VARCHAR, 
    host_user_email VARCHAR, 
    share_secret VARCHAR, 
    strategy_keys_id INTEGER, 
    strategy_code VARCHAR, 
    order_count_type INTEGER, 
    dynamic_calculation_type INTEGER DEFAULT '1', 
    strategy_amount NUMERIC, 
    position_amount NUMERIC, 
    allocation_amount NUMERIC, 
    can_use_amount NUMERIC, 
    accruing_amounts NUMERIC, 
    enable INTEGER DEFAULT '1', 
    days_number INTEGER, 
    is_open INTEGER DEFAULT '0', 
    delete_time DATETIME, 
    start_time DATETIME, 
    service_charge NUMERIC, 
    lower_limit_of_fees NUMERIC, 
    backtest_id INTEGER, 
    mock_service_charge NUMERIC, 
    mock_lower_limit_of_fees NUMERIC, 
    mock_allocation_amount NUMERIC, 
    user_id VARCHAR, 
    is_simulation INTEGER DEFAULT '0', 
    platform INTEGER DEFAULT '1', 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE trades (
    order_id INTEGER, 
    order_sysid VARCHAR, 
    stock_code VARCHAR, 
    traded_volume INTEGER, 
    traded_time INTEGER, 
    traded_price NUMERIC, 
    traded_amount NUMERIC, 
    commission NUMERIC, 
    order_status INTEGER, 
    order_type INTEGER, 
    status_msg VARCHAR, 
    offset_flag INTEGER, 
    orders_id INTEGER, 
    task_id INTEGER, 
    status INTEGER DEFAULT '0', 
    backtest_id INTEGER, 
    is_mock INTEGER DEFAULT '0', 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE INDEX ix_trades_is_mock ON trades (is_mock);

INSERT INTO alembic_version (version_num) VALUES ('9b65683001b8') RETURNING version_num;

-- Running upgrade 9b65683001b8 -> a4e1e167b159

UPDATE alembic_version SET version_num='a4e1e167b159' WHERE alembic_version.version_num = '9b65683001b8';

-- Running upgrade a4e1e167b159 -> 6badaf17893b

CREATE TABLE remote_positions (
    security_code VARCHAR, 
    volume INTEGER, 
    task_id INTEGER, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

UPDATE alembic_version SET version_num='6badaf17893b' WHERE alembic_version.version_num = 'a4e1e167b159';

-- Running upgrade 6badaf17893b -> 1a69ebe0c486

UPDATE alembic_version SET version_num='1a69ebe0c486' WHERE alembic_version.version_num = '6badaf17893b';

-- Running upgrade 1a69ebe0c486 -> 07ab3e87c195

ALTER TABLE tasklist ADD COLUMN position_ratio NUMERIC DEFAULT '1';

UPDATE alembic_version SET version_num='07ab3e87c195' WHERE alembic_version.version_num = '1a69ebe0c486';

-- Running upgrade 07ab3e87c195 -> 1dfc206b5893

ALTER TABLE tasklist ADD COLUMN open_mandatory_limit_order INTEGER DEFAULT '0';

UPDATE alembic_version SET version_num='1dfc206b5893' WHERE alembic_version.version_num = '07ab3e87c195';


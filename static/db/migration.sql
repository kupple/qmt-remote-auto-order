CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 96ee93975f8a

INSERT INTO alembic_version (version_num) VALUES ('96ee93975f8a') RETURNING version_num;

-- Running upgrade 96ee93975f8a -> a69c80be508b

CREATE TABLE ppx_storage_var (
    id INTEGER NOT NULL, 
    "key" VARCHAR NOT NULL, 
    val VARCHAR DEFAULT '' NOT NULL, 
    remark VARCHAR DEFAULT '' NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE INDEX ix_ppx_storage_var_key ON ppx_storage_var ("key");

UPDATE alembic_version SET version_num='a69c80be508b' WHERE alembic_version.version_num = '96ee93975f8a';

-- Running upgrade a69c80be508b -> a681e6d08085

UPDATE alembic_version SET version_num='a681e6d08085' WHERE alembic_version.version_num = 'a69c80be508b';

-- Running upgrade a681e6d08085 -> 893f6c585cd2

ALTER TABLE ppx_storage_var ADD COLUMN remark2 VARCHAR DEFAULT '' NOT NULL;

UPDATE alembic_version SET version_num='893f6c585cd2' WHERE alembic_version.version_num = 'a681e6d08085';

-- Running upgrade 893f6c585cd2 -> b43147be6240

ALTER TABLE ppx_storage_var DROP COLUMN remark2;

UPDATE alembic_version SET version_num='b43147be6240' WHERE alembic_version.version_num = '893f6c585cd2';

-- Running upgrade b43147be6240 -> 15582046f382

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
    id INTEGER NOT NULL, 
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
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE setting (
    python_path VARCHAR, 
    mini_qmt_path VARCHAR, 
    client_id VARCHAR, 
    salt VARCHAR, 
    server_url VARCHAR, 
    run_model_type INTEGER DEFAULT '0', 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE tasklist (
    name VARCHAR, 
    strategy_code VARCHAR, 
    order_count_type INTEGER, 
    strategy_amount INTEGER, 
    allocation_amount INTEGER, 
    enable INTEGER DEFAULT '1', 
    days_number INTEGER, 
    is_open INTEGER DEFAULT '0', 
    delete_time DATETIME, 
    start_time DATETIME, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

CREATE TABLE trades (
    order_id INTEGER, 
    order_sysid VARCHAR, 
    order_time INTEGER, 
    order_volume INTEGER, 
    price_type INTEGER, 
    price NUMERIC, 
    traded_volume NUMERIC, 
    traded_price NUMERIC, 
    order_status INTEGER, 
    status_msg VARCHAR, 
    offset_flag INTEGER, 
    orders_id INTEGER, 
    status INTEGER DEFAULT '0', 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

UPDATE alembic_version SET version_num='15582046f382' WHERE alembic_version.version_num = 'b43147be6240';

-- Running upgrade 15582046f382 -> b0aeb5a4cef5

UPDATE alembic_version SET version_num='b0aeb5a4cef5' WHERE alembic_version.version_num = '15582046f382';

-- Running upgrade b0aeb5a4cef5 -> 523683b9b2e8

UPDATE alembic_version SET version_num='523683b9b2e8' WHERE alembic_version.version_num = 'b0aeb5a4cef5';

-- Running upgrade 523683b9b2e8 -> 5c506eb4d39e

ALTER TABLE setting ADD COLUMN auto_national_debt INTEGER DEFAULT '0';

UPDATE alembic_version SET version_num='5c506eb4d39e' WHERE alembic_version.version_num = '523683b9b2e8';

-- Running upgrade 5c506eb4d39e -> 1aa18a798069

ALTER TABLE setting ADD COLUMN auto_buy_stock_ipo INTEGER DEFAULT '0';

ALTER TABLE setting ADD COLUMN auto_buy_purchase_ipo INTEGER DEFAULT '0';

UPDATE alembic_version SET version_num='1aa18a798069' WHERE alembic_version.version_num = '5c506eb4d39e';

-- Running upgrade 1aa18a798069 -> 9b3c8e5abf11

ALTER TABLE setting ADD COLUMN account VARCHAR;

UPDATE alembic_version SET version_num='9b3c8e5abf11' WHERE alembic_version.version_num = '1aa18a798069';

-- Running upgrade 9b3c8e5abf11 -> 1f921a4f9c15

CREATE TABLE position (
    security_code VARCHAR, 
    volume INTEGER, 
    amount NUMERIC, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

ALTER TABLE tasklist ADD COLUMN position_amount INTEGER;

UPDATE alembic_version SET version_num='1f921a4f9c15' WHERE alembic_version.version_num = '9b3c8e5abf11';

-- Running upgrade 1f921a4f9c15 -> 532942a6e3c4

CREATE TABLE positions (
    security_code VARCHAR, 
    volume INTEGER, 
    amount NUMERIC, 
    id INTEGER NOT NULL, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

DROP TABLE position;

UPDATE alembic_version SET version_num='532942a6e3c4' WHERE alembic_version.version_num = '1f921a4f9c15';

-- Running upgrade 532942a6e3c4 -> 665c2306314e

ALTER TABLE setting ADD COLUMN auto_startup INTEGER DEFAULT '0';

UPDATE alembic_version SET version_num='665c2306314e' WHERE alembic_version.version_num = '532942a6e3c4';

-- Running upgrade 665c2306314e -> 0beac3d413f5

ALTER TABLE tasklist ADD COLUMN service_charge NUMERIC;

ALTER TABLE tasklist ADD COLUMN lower_limit_of_fees NUMERIC;

UPDATE alembic_version SET version_num='0beac3d413f5' WHERE alembic_version.version_num = '665c2306314e';

-- Running upgrade 0beac3d413f5 -> a4f715ab4b80

ALTER TABLE positions ADD COLUMN task_id INTEGER;

UPDATE alembic_version SET version_num='a4f715ab4b80' WHERE alembic_version.version_num = '0beac3d413f5';

-- Running upgrade a4f715ab4b80 -> 84093fc6bb19

CREATE TABLE backtest (
    id INTEGER NOT NULL, 
    start_time DATETIME, 
    service_charge NUMERIC, 
    initial_amount NUMERIC, 
    final_amount NUMERIC, 
    task_id INTEGER, 
    created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    updated_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'localtime')), 
    PRIMARY KEY (id)
);

ALTER TABLE tasklist ADD COLUMN backtest_id INTEGER;

UPDATE alembic_version SET version_num='84093fc6bb19' WHERE alembic_version.version_num = 'a4f715ab4b80';

-- Running upgrade 84093fc6bb19 -> d0a534f62656

ALTER TABLE entrusts ADD COLUMN backtest_id INTEGER;

ALTER TABLE orders ADD COLUMN backtest_id INTEGER;

ALTER TABLE positions ADD COLUMN backtest_id INTEGER;

ALTER TABLE trades ADD COLUMN backtest_id INTEGER;

UPDATE alembic_version SET version_num='d0a534f62656' WHERE alembic_version.version_num = '84093fc6bb19';

-- Running upgrade d0a534f62656 -> d00d4466cc95

ALTER TABLE backtest ADD COLUMN name VARCHAR;

ALTER TABLE backtest ADD COLUMN frequency VARCHAR;

UPDATE alembic_version SET version_num='d00d4466cc95' WHERE alembic_version.version_num = 'd0a534f62656';

-- Running upgrade d00d4466cc95 -> dac0eafcee97

ALTER TABLE backtest ADD COLUMN initial_capital NUMERIC;

ALTER TABLE backtest ADD COLUMN lower_limit_of_fees NUMERIC;

ALTER TABLE backtest DROP COLUMN initial_amount;

UPDATE alembic_version SET version_num='dac0eafcee97' WHERE alembic_version.version_num = 'd00d4466cc95';

-- Running upgrade dac0eafcee97 -> 2fa8af85fa19

ALTER TABLE backtest ADD COLUMN state VARCHAR;

UPDATE alembic_version SET version_num='2fa8af85fa19' WHERE alembic_version.version_num = 'dac0eafcee97';

-- Running upgrade 2fa8af85fa19 -> 529782e3dade

ALTER TABLE backtest DROP COLUMN start_time;

ALTER TABLE positions ADD COLUMN delete_time DATETIME;

UPDATE alembic_version SET version_num='529782e3dade' WHERE alembic_version.version_num = '2fa8af85fa19';

-- Running upgrade 529782e3dade -> e0c2edd701ce

ALTER TABLE trades ADD COLUMN traded_amount NUMERIC;

ALTER TABLE trades DROP COLUMN price;

ALTER TABLE trades DROP COLUMN price_type;

ALTER TABLE trades DROP COLUMN order_volume;

ALTER TABLE trades DROP COLUMN order_time;

UPDATE alembic_version SET version_num='e0c2edd701ce' WHERE alembic_version.version_num = '529782e3dade';

-- Running upgrade e0c2edd701ce -> 98f4f321d568

ALTER TABLE trades ADD COLUMN order_type INTEGER;

UPDATE alembic_version SET version_num='98f4f321d568' WHERE alembic_version.version_num = 'e0c2edd701ce';

-- Running upgrade 98f4f321d568 -> 0c14bb355caa

ALTER TABLE trades ADD COLUMN stock_code VARCHAR;

UPDATE alembic_version SET version_num='0c14bb355caa' WHERE alembic_version.version_num = '98f4f321d568';

-- Running upgrade 0c14bb355caa -> ba7814e60edb

ALTER TABLE trades ADD COLUMN traded_time INTEGER;

UPDATE alembic_version SET version_num='ba7814e60edb' WHERE alembic_version.version_num = '0c14bb355caa';

-- Running upgrade ba7814e60edb -> cf01b55a1307

ALTER TABLE tasklist ADD COLUMN dynamic_calculation_type INTEGER;

UPDATE alembic_version SET version_num='cf01b55a1307' WHERE alembic_version.version_num = 'ba7814e60edb';

-- Running upgrade cf01b55a1307 -> 4b30d3ff9ca0

UPDATE alembic_version SET version_num='4b30d3ff9ca0' WHERE alembic_version.version_num = 'cf01b55a1307';

-- Running upgrade 4b30d3ff9ca0 -> b0ec1d0d11aa

ALTER TABLE tasklist ADD COLUMN mock_service_charge NUMERIC;

ALTER TABLE tasklist ADD COLUMN mock_lower_limit_of_fees NUMERIC;

UPDATE alembic_version SET version_num='b0ec1d0d11aa' WHERE alembic_version.version_num = '4b30d3ff9ca0';

-- Running upgrade b0ec1d0d11aa -> 5f389173a5d8

ALTER TABLE tasklist ADD COLUMN mock_allocation_amount NUMERIC;

UPDATE alembic_version SET version_num='5f389173a5d8' WHERE alembic_version.version_num = 'b0ec1d0d11aa';

-- Running upgrade 5f389173a5d8 -> 19ff43303ec2

UPDATE alembic_version SET version_num='19ff43303ec2' WHERE alembic_version.version_num = '5f389173a5d8';

-- Running upgrade 19ff43303ec2 -> 1fb8c8dc58e3

ALTER TABLE entrusts ADD COLUMN is_mock INTEGER DEFAULT '0';

ALTER TABLE orders ADD COLUMN is_mock INTEGER DEFAULT '0';

ALTER TABLE positions ADD COLUMN is_mock INTEGER DEFAULT '0';

ALTER TABLE trades ADD COLUMN is_mock INTEGER DEFAULT '0';

UPDATE alembic_version SET version_num='1fb8c8dc58e3' WHERE alembic_version.version_num = '19ff43303ec2';

-- Running upgrade 1fb8c8dc58e3 -> 070a4abaf019

CREATE INDEX ix_entrusts_is_mock ON entrusts (is_mock);

CREATE INDEX ix_orders_is_mock ON orders (is_mock);

CREATE INDEX ix_positions_is_mock ON positions (is_mock);

CREATE INDEX ix_trades_is_mock ON trades (is_mock);

UPDATE alembic_version SET version_num='070a4abaf019' WHERE alembic_version.version_num = '1fb8c8dc58e3';

-- Running upgrade 070a4abaf019 -> aa39b00cc416

ALTER TABLE backtest ADD COLUMN accruing_amounts NUMERIC;

ALTER TABLE tasklist ADD COLUMN accruing_amounts NUMERIC;

UPDATE alembic_version SET version_num='aa39b00cc416' WHERE alembic_version.version_num = '070a4abaf019';

-- Running upgrade aa39b00cc416 -> 895b0cf90a97

ALTER TABLE positions ADD COLUMN average_price NUMERIC;

UPDATE alembic_version SET version_num='895b0cf90a97' WHERE alembic_version.version_num = 'aa39b00cc416';

-- Running upgrade 895b0cf90a97 -> 61f020288394

ALTER TABLE orders ADD COLUMN positions VARCHAR;

UPDATE alembic_version SET version_num='61f020288394' WHERE alembic_version.version_num = '895b0cf90a97';

-- Running upgrade 61f020288394 -> e4f130d89eb8

ALTER TABLE backtest ADD COLUMN can_use_amount NUMERIC;

ALTER TABLE tasklist ADD COLUMN can_use_amount NUMERIC;

UPDATE alembic_version SET version_num='e4f130d89eb8' WHERE alembic_version.version_num = '61f020288394';

-- Running upgrade e4f130d89eb8 -> d358634f863f

UPDATE alembic_version SET version_num='d358634f863f' WHERE alembic_version.version_num = 'e4f130d89eb8';

-- Running upgrade d358634f863f -> 0cd5bf054f8d

UPDATE alembic_version SET version_num='0cd5bf054f8d' WHERE alembic_version.version_num = 'd358634f863f';

-- Running upgrade 0cd5bf054f8d -> 549dea92950f

ALTER TABLE backtest ADD COLUMN order_count_type INTEGER;

UPDATE alembic_version SET version_num='549dea92950f' WHERE alembic_version.version_num = '0cd5bf054f8d';

-- Running upgrade 549dea92950f -> c973f5f9682c

UPDATE alembic_version SET version_num='c973f5f9682c' WHERE alembic_version.version_num = '549dea92950f';

-- Running upgrade c973f5f9682c -> 09f54fab8f5b

ALTER TABLE trades ADD COLUMN task_id INTEGER;

UPDATE alembic_version SET version_num='09f54fab8f5b' WHERE alembic_version.version_num = 'c973f5f9682c';

-- Running upgrade 09f54fab8f5b -> bd9f4edc43f0

ALTER TABLE tasklist ADD COLUMN task_type INTEGER DEFAULT '1';

UPDATE alembic_version SET version_num='bd9f4edc43f0' WHERE alembic_version.version_num = '09f54fab8f5b';

-- Running upgrade bd9f4edc43f0 -> a5f04056d6dd

ALTER TABLE tasklist ADD COLUMN share_secret VARCHAR;

UPDATE alembic_version SET version_num='a5f04056d6dd' WHERE alembic_version.version_num = 'bd9f4edc43f0';

-- Running upgrade a5f04056d6dd -> 250b87dde449

ALTER TABLE tasklist ADD COLUMN come_form_str VARCHAR;

UPDATE alembic_version SET version_num='250b87dde449' WHERE alembic_version.version_num = 'a5f04056d6dd';


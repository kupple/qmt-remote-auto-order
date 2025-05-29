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


CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> fa5bf4cff82d

ALTER TABLE tasklist ALTER COLUMN platform SET NOT NULL;

INSERT INTO alembic_version (version_num) VALUES ('fa5bf4cff82d') RETURNING version_num;

-- Running upgrade fa5bf4cff82d -> 98bd86d5740d

ALTER TABLE tasklist ADD COLUMN platform INTEGER DEFAULT '1' NOT NULL;

UPDATE alembic_version SET version_num='98bd86d5740d' WHERE alembic_version.version_num = 'fa5bf4cff82d';


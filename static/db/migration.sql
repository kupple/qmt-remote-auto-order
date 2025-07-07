CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> fa5bf4cff82d

INSERT INTO alembic_version (version_num) VALUES ('fa5bf4cff82d') RETURNING version_num;

-- Running upgrade fa5bf4cff82d -> 98bd86d5740d

UPDATE alembic_version SET version_num='98bd86d5740d' WHERE alembic_version.version_num = 'fa5bf4cff82d';

-- Running upgrade 98bd86d5740d -> 4440b066fce2

UPDATE alembic_version SET version_num='4440b066fce2' WHERE alembic_version.version_num = '98bd86d5740d';


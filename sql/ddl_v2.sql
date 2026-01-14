-- recurrink data model v2

DROP TABLE models CASCADE;
CREATE TABLE models (
  mid serial PRIMARY KEY,
  model VARCHAR(50)
);

DROP TABLE inkpal CASCADE;
CREATE TABLE inkpal (
  ver serial PRIMARY KEY,
  gplfile VARCHAR(50)
);

INSERT into INKPAL (gplfile)
VALUES
  ('uniball'),
  ('copicsketch'),
  ('copic'),
  ('stabilo68'),
  ('sharpie'),
  ('staedtler');


DROP TABLE pens CASCADE;
CREATE TABLE pens (
  ver INT,
  fill VARCHAR(7) CHECK (fill ~* '^#[a-f0-9]{6}$'),  -- enforce once
  penam VARCHAR(50),
  FOREIGN KEY (ver) REFERENCES inkpal (ver),
  UNIQUE (ver, fill)
);

-- guide rink generation from model
DROP TABLE compass;
CREATE TABLE compass (
  mid INT,
  cell CHAR(1) NOT NULL,
  pair CHAR(1),
  facing VARCHAR(2) NOT NULL,
  FOREIGN KEY (mid) REFERENCES models (mid)
);
DROP TABLE blocks;
CREATE TABLE blocks (
  mid INT,
  position INT [] NOT NULL,
  cell CHAR(1) NOT NULL,
  top CHAR(1),
  FOREIGN KEY (mid) REFERENCES models (mid),
  UNIQUE (mid, position)
);

-- an instance of a model is rink
DROP TABLE rinks CASCADE;
CREATE TABLE rinks (
  rinkid CHAR(32) PRIMARY KEY,     -- assume digest makes unique IDs
  mid INT NOT NULL,
  ver INT NOT NULL,
  clen INT,
  factor NUMERIC(3,2),
  created timestamp DEFAULT current_timestamp,
  pubdate timestamp,
  FOREIGN KEY (mid) REFERENCES models (mid),
  FOREIGN KEY (ver) REFERENCES inkpal (ver),
  UNIQUE (rinkid)
);

DROP TABLE geometry CASCADE;
CREATE TABLE geometry (
  rinkid CHAR(32) NOT NULL,
  cell CHAR(1) NOT NULL,
  layer SMALLINT NOT NULL,
  name VARCHAR(7),
  size VARCHAR(7),
  facing VARCHAR(2),
  FOREIGN KEY (rinkid) REFERENCES rinks (rinkid),
  UNIQUE (rinkid, cell, layer)
);

DROP TABLE strokes CASCADE;
CREATE TABLE strokes (
  rinkid CHAR(32) NOT NULL,
  cell CHAR(1) NOT NULL,
  layer SMALLINT NOT NULL,
  ver INT NOT NULL,
  fill VARCHAR(7),
  opacity FLOAT DEFAULT 1.0,
  width INT DEFAULT 0,
  dasharray INT DEFAULT 0,
  FOREIGN KEY (rinkid) REFERENCES rinks (rinkid),
  UNIQUE (rinkid, cell, layer)
);

DROP TABLE palette;
CREATE TABLE palette (
  rinkid CHAR(32) NOT NULL,
  cell CHAR(1) NOT NULL,
  layer SMALLINT NOT NULL,
  ver INT NOT NULL,
  fill VARCHAR(7),
  opacity FLOAT DEFAULT 1.0,
  FOREIGN KEY (rinkid) REFERENCES rinks (rinkid),
  FOREIGN KEY (ver) REFERENCES inkpal (ver),
  UNIQUE (rinkid, cell, layer)
);

-- the end

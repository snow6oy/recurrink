-- recurrink POC


DROP TABLE geometry CASCADE;
DROP TYPE sizes;
DROP TYPE direction;
CREATE TYPE sizes as ENUM ('large', 'medium', 'small');
CREATE TYPE direction as ENUM ('all', 'north', 'south', 'east', 'west');

-- Geometry ID +:1 one Geom many positions
CREATE TABLE geometry (
  GID serial PRIMARY KEY,
  shape VARCHAR(50) NOT NULL,
  size sizes DEFAULT 'medium',
  facing direction NOT NULL,
  top BOOLEAN DEFAULT FALSE,
  UNIQUE (shape, size, facing)
);

DROP TABLE styles CASCADE;
-- Styles ID +:1 one Style many positions
-- fill and bg are mandated
CREATE TABLE styles (
  SID serial PRIMARY KEY,
  fill VARCHAR(50) NOT NULL,
  bg VARCHAR(50) NOT NULL,
  fill_opacity FLOAT DEFAULT 1.0,
  stroke VARCHAR(50) DEFAULT '#000',
  stroke_width INT DEFAULT 1,
  stroke_dasharray INT DEFAULT 0,
  stroke_opacity FLOAT DEFAULT 1.0
);

DROP TABLE models CASCADE;
-- Model metadata
CREATE TABLE models (
  model VARCHAR(50) PRIMARY KEY,
  uniqcells INT NOT NULL,
  blocksizeXY INT[] NOT NULL,
  scale FLOAT NOT NULL
);

-- position has a 1:1 relation with Geometry and Styles linked by Cell
DROP TABLE blocks;

CREATE TABLE blocks (
  model VARCHAR(50) NOT NULL,
  position INT [] NOT NULL,
  cell CHAR(1) NOT NULL,
  FOREIGN KEY (model) REFERENCES models (model),
  UNIQUE (model, position)
);

DROP TABLE views CASCADE;
DROP TYPE authors;
CREATE TYPE authors as ENUM ('human', 'machine');

-- view is a model instance
-- each cell is a tuple containing [Pos, Geom, Style]
CREATE TABLE views (
  view VARCHAR(50) NOT NULL,
  cell CHAR(1) NOT NULL,
  model VARCHAR(50) NOT NULL,
  author authors DEFAULT 'human',
  SID INT NOT NULL,
  GID INT NOT NULL,
  FOREIGN KEY (model) REFERENCES models (model),
  FOREIGN KEY (SID) REFERENCES styles (SID),
  FOREIGN KEY (GID) REFERENCES geometry (GID),
  UNIQUE (view, cell)
);

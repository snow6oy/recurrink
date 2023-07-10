-- recurrink data model

DROP TABLE geometry CASCADE;
DROP TYPE shapes;
DROP TYPE sizes;
DROP TYPE direction;
CREATE TYPE sizes as ENUM ('large', 'medium', 'small');
CREATE TYPE direction as ENUM ('all', 'north', 'south', 'east', 'west');
-- dropped shapes in favor CHAR(7) and NOT NULL
-- CREATE TYPE shapes as ENUM ('circle', 'line', 'square', 'triangle', 'diamond');

-- Geometry ID +:1 one Geom many positions
CREATE TABLE geometry (
  GID serial PRIMARY KEY,
  shape shapes NOT NULL,
  size sizes DEFAULT 'medium',
  facing direction NOT NULL,
  top BOOLEAN DEFAULT FALSE,
  UNIQUE (shape, size, facing)
);

DROP TABLE styles CASCADE;
DROP TYPE fill;
CREATE TYPE fill as ENUM ('#FFF','#CCC','#CD5C5C','#000','#FFA500','#DC143C','#C71585','#4B0082','#32CD32','#9ACD32');

-- Styles ID +:1 one Style many positions
-- fill and bg are mandated
CREATE TABLE styles (
  SID serial PRIMARY KEY,
  fill fill NOT NULL,
  bg fill NOT NULL,
  fill_opacity FLOAT DEFAULT 1.0,
  stroke fill DEFAULT '#000',
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
CREATE TABLE views (
  view VARCHAR(50) PRIMARY KEY,
  model VARCHAR(50) NOT NULL,
  author authors DEFAULT 'human',
  control INT NOT NULL DEFAULT 0,
  created timestamp DEFAULT current_timestamp,
  FOREIGN KEY (model) REFERENCES models (model)
);

DROP TABLE cells;
-- a cell is a tuple containing [blocks.position+, geometry.gid, styles.sid]
CREATE TABLE cells (
  view VARCHAR(50) NOT NULL,
  cell CHAR(1) NOT NULL,
  sid INT NOT NULL,
  gid INT NOT NULL,
  FOREIGN KEY (view) REFERENCES views (view),
  FOREIGN KEY (SID) REFERENCES styles (SID),
  FOREIGN KEY (GID) REFERENCES geometry (GID),
  UNIQUE (view, cell)
);

-- temporary for data cleaning
-- CREATE TABLE files ( view CHAR(32) PRIMARY KEY, model VARCHAR(50) NOT NULL);

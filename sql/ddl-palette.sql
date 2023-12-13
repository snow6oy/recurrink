-- recurrink extended with palette

DROP TABLE colours CASCADE;
CREATE TABLE colours (
  fill VARCHAR(7) CHECK (fill ~* '^#[A-F0-9]{3,6}$'),
  UNIQUE (fill)
);

DROP TABLE strokes;
CREATE TABLE strokes (
  sid serial PRIMARY KEY,
  fill VARCHAR(7),
  width INT DEFAULT 1,
  dasharray INT DEFAULT 0,
  opacity FLOAT DEFAULT 1.0,
  FOREIGN KEY (fill) REFERENCES colours (fill)
);
-- ver 
--   0 universal
--   1 colour45
--   2 htmstarter
DROP TABLE palette;
CREATE TABLE palette (
  pid serial PRIMARY KEY,
  ver INT NOT NULL,
  fill VARCHAR(7),
  bg VARCHAR(7),
  complimentary VARCHAR(7),
  opacity FLOAT DEFAULT 1.0,
  FOREIGN KEY (fill) REFERENCES colours (fill),
  FOREIGN KEY (bg) REFERENCES colours (fill),
  FOREIGN KEY (complimentary) REFERENCES colours (fill)
);

DROP TABLE cells_new;
CREATE TABLE cells_new (
  view CHAR(32) NOT NULL,
  cell CHAR(1) NOT NULL,
  gid INT NOT NULL,
  pid INT NOT NULL,
  sid INT NULL,  -- stroke id
  FOREIGN KEY (view) REFERENCES views (view),
  FOREIGN KEY (GID) REFERENCES geometry (GID),
  FOREIGN KEY (PID) REFERENCES palette (PID),
  FOREIGN KEY (SID) REFERENCES strokes (SID),
  UNIQUE (view, cell)
);

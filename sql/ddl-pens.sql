-- original palette was hard to use
-- this version has fewer constraints
-- and new field (pen name) to help plotting

-- from config.py
DROP TABLE inkpal CASCADE;
CREATE TABLE inkpal (
  ver serial PRIMARY KEY,
  gplfile VARCHAR(15)
);

-- from inkscape GPL file

INSERT into INKPAL (gplfile)
VALUES
  ('universal'),
  ('colour45'), 
  ('htmstarter'), 
  ('jeb'), 
  ('whitebossa'), 
  ('snowbg'), 
  ('solar'),
  ('uniball'),
  ('copic_sketch'),
  ('copic'),
  ('stabilo68');

DROP TABLE pens;
CREATE TABLE pens (
  ver INT NOT NULL,
  fill VARCHAR(7) CHECK (fill ~* '^#[a-fA-F0-9]{3,6}$'),
  penam VARCHAR(15),
  PRIMARY KEY (ver, fill),
  FOREIGN KEY (ver) REFERENCES inkpal (ver)
);

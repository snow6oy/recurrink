-- Schema for Recipe table
-- direction as ENUM ('all', 'north', 'south', 'east', 'west');
-- TODO add northeast southwest
--ALTER TYPE direction ADD VALUE 'northeast';
-- ALTER TYPE direction ADD VALUE 'southwest';
DROP TABLE compass;

CREATE TABLE compass (
  model VARCHAR(50) NOT NULL,
  cell CHAR(1) NOT NULL,
  pair CHAR(1),
  facing direction NOT NULL,
  FOREIGN KEY (model) REFERENCES models (model)
);

INSERT INTO compass (model, cell, pair, facing)
VALUES
  ('syncopated', 'i', null, 'all'),
  ('syncopated', 'j', null, 'all'),
  ('syncopated', 'a', 'b', 'north'),
  ('syncopated', 'g', 'h', 'north'),
  ('syncopated', 'c', 'd', 'north'),
  ('syncopated', 'e', 'f', 'north'),
  ('marchingband', 'e', null, 'all'),
  ('marchingband', 'f', null, 'all'),
  ('marchingband', 'b', 'c', 'north'),
  ('marchingband', 'a', 'd', 'east'),
  ('timpani', 'e', null, 'all'),
  ('timpani', 'f', null, 'all'),
  ('timpani', 'k', null, 'all'),
  ('timpani', 'a', 'b', 'northeast'),
  ('timpani', 'c', 'd', 'northeast'),
  ('timpani', 'g', 'h', 'northeast'),
  ('timpani', 'i', 'j', 'northeast'),
  ('soleares', 'a', null, 'all'),
  ('soleares', 'c', null, 'all'),
  ('soleares', 'b', 'd', 'east'),
  ('koto', 'e', null, 'all'),
  ('koto', 'f', null, 'all'),
  ('koto', 'g', null, 'all'),
  ('koto', 'b', 'c', 'northeast'),
  ('koto', 'a', 'd', 'southwest'),
  ('waltz', 'a', 'b', 'north'),
  ('waltz', 'c', 'd', 'north'),
  ('eflat', 'c', 'f', 'northeast'),
  ('eflat', 'b', 'g', 'northeast'),
  ('eflat', 'e', 'd', 'east'),
  ('eflat', 'a', null, 'all'),
  ('mambo', 'x', null, 'all'),
  ('mambo', 'e', 'o', 'east'),
  ('mambo', 'a', 'b', 'north'),
  ('tumbao', 'a', 'f', 'northeast'),
  ('tumbao', 'b', null, 'all'),
  ('tumbao', 'c', 'e', 'northeast'),
  ('tumbao', 'd', null, 'all'),
  ('tumbao', 'e', 'c', 'northeast'),
  ('tumbao', 'f', 'a', 'northeast');

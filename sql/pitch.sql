-- INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
--   VALUES ('pitch', 9, '{6, 6}', 1.0);

INSERT INTO compass (model, cell, pair, facing)
VALUES
  ('pitch', 'a', null, 'all'),
  ('pitch', 'b', null, 'all'),
  ('pitch', 'c', null, 'all'),
  ('pitch', 'd', null, 'all'),
  ('pitch', 'e', 'j', 'southwest'),
  ('pitch', 'f', null, 'all'),
  ('pitch', 'g', 'h', 'southwest');

INSERT INTO blocks (model, position, cell, top) 
VALUES 
  ('pitch', '{0,0}', 'a', null),
  ('pitch', '{2,2}', 'a', null),
  ('pitch', '{3,3}', 'a', null),
  ('pitch', '{5,5}', 'a', null),
  ('pitch', '{1,0}', 'b', null),
  ('pitch', '{0,1}', 'b', null),
  ('pitch', '{4,3}', 'b', null),
  ('pitch', '{3,4}', 'b', null),
  ('pitch', '{2,0}', 'c', null),
  ('pitch', '{0,2}', 'c', null),
  ('pitch', '{5,3}', 'c', null),
  ('pitch', '{3,5}', 'c', null),
  ('pitch', '{3,0}', 'd', null),
  ('pitch', '{5,2}', 'd', null),
  ('pitch', '{0,3}', 'd', null),
  ('pitch', '{2,5}', 'd', null),
  ('pitch', '{4,0}', 'e', null),
  ('pitch', '{1,1}', 'e', null),
  ('pitch', '{5,1}', 'e', null),
  ('pitch', '{4,2}', 'e', null),
  ('pitch', '{1,3}', 'e', null),
  ('pitch', '{2,4}', 'e', null),
  ('pitch', '{4,4}', 'e', null),
  ('pitch', '{1,5}', 'e', null),
  ('pitch', '{5,0}', 'f', null),
  ('pitch', '{3,2}', 'f', null),
  ('pitch', '{2,3}', 'f', null),
  ('pitch', '{0,5}', 'f', null),
  ('pitch', '{2,1}', 'g', 'h'),
  ('pitch', '{5,4}', 'g', 'h'),
  ('pitch', '{3,1}', 'j', 'e'),
  ('pitch', '{0,4}', 'j', 'e'),
  ('pitch', '{4,1}', 'h', null),
  ('pitch', '{1,2}', 'h', null),
  ('pitch', '{1,4}', 'h', null),
  ('pitch', '{4,5}', 'h', null);

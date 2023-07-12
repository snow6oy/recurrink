-- testcard data
-- DEFAULTS size: medium top:FALSE
UPDATE geometry
SET shape='square', size='small', facing='all', top=DEFAULT
WHERE gid=2;
UPDATE geometry
SET shape='circle', size='small', facing='all', top=DEFAULT
WHERE gid=4;

INSERT INTO geometry (shape, size, facing, top) 
VALUES 
  ('line', 'small', 'north', DEFAULT),
  ('line', 'small', 'east', DEFAULT);

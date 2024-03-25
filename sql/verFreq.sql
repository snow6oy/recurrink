-- views with pids in universal
SELECT distinct(view) as v, count(distinct(palette.pid)) as pnum
FROM palette
LEFT JOIN cells ON cells.pid = palette.pid
WHERE ver = 0
GROUP BY v
ORDER BY pnum ASC

-- frequency of versions in views
-- SELECT count(ver), ver 
-- FROM views 
-- GROUP BY ver;

-- unused pids in universal
-- SELECT palette.pid
-- FROM palette
-- LEFT JOIN cells ON cells.pid = palette.pid
-- WHERE cells.pid IS NULL
-- AND ver = 0


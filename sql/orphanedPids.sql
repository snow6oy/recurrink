-- 
SELECT p.pid, ver,  fill,   bg, opacity, relation 
FROM palette p
LEFT JOIN cells c ON c.pid = p.pid
WHERE c.pid IS NULL
ORDER BY ver

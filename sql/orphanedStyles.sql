
-- list styles that are orphaned, i.e. not referenced in the cells table
SELECT s.sid
FROM styles s
LEFT JOIN cells c ON c.sid = s.sid
WHERE c.sid IS NULL

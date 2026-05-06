SELECT count(*) as freq, model
FROM rinks, models
WHERE rinks.mid = models.mid
GROUP BY model ORDER BY freq;

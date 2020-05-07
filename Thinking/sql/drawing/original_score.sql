WITH data_freq AS( 
	SELECT `Data`, 
	COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS freq 
	FROM drawing 
	GROUP BY `Data` 
) 
SELECT drawing.crtuser, drawing.`Data`, data_freq.freq 
FROM data_freq, drawing 
WHERE drawing.`Data` = data_freq.`Data`;
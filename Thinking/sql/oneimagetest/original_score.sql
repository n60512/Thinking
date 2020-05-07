WITH data_freq AS( 
	SELECT `Data`, 
	COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS freq 
	FROM oneimagetest 
	GROUP BY `Data` 
) 
SELECT oneimagetest.crtuser, oneimagetest.`Data`, data_freq.freq 
FROM data_freq, oneimagetest 
WHERE oneimagetest.`Data` = data_freq.`Data`;
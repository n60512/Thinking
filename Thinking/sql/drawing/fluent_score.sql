SELECT `crtuser`, count(`crtuser`)
FROM drawing 

WHERE drawing.`Name` NOT LIKE '' 
AND drawing.`Name` NOT LIKE '% %' 
AND drawing.`Name` NOT LIKE '%,%' 
GROUP by crtuser 
ORDER BY crtuser 
;

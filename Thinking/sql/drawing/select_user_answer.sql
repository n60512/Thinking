SELECT DrawingNO AS `ID`, `crtuser`, `Name` AS `text` 
FROM drawing 

WHERE drawing.`Name` NOT LIKE '' 
AND drawing.`Name` NOT LIKE '% %' 
AND drawing.`Name` NOT LIKE '%,%' 
ORDER BY crtuser, `Name` 
;

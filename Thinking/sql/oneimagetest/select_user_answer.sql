WITH correct_table AS ( 
	SELECT `Data` FROM oneimagetest_wrong WHERE correct = 'N' 
) 
SELECT oneImageTestNO AS `ID`, `crtuser`, `Data` AS `text` 
FROM oneimagetest 
WHERE oneimagetest.`Data` NOT IN ( 
	SELECT * FROM correct_table 
	) 
AND oneimagetest.`Data` NOT LIKE '' 
AND oneimagetest.`Data` NOT LIKE '% %' 
AND oneimagetest.`Data` NOT LIKE '%,%' 
ORDER BY crtuser, `Data` 
;

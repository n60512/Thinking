WITH incorrect_table AS ( 
	SELECT `Data` FROM oneimagetest_wrong WHERE correct = 'N' 
) 
SELECT `crtuser`, count(`crtuser`)
FROM oneimagetest 
WHERE oneimagetest.`Data` NOT IN ( 
	SELECT * FROM incorrect_table 
	) 
AND oneimagetest.`Data` NOT LIKE '' 
AND oneimagetest.`Data` NOT LIKE '% %' 
AND oneimagetest.`Data` NOT LIKE '%,%' 
GROUP by crtuser 
ORDER BY crtuser 
;
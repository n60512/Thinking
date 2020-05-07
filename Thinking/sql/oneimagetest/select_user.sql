WITH correct_table AS ( 
	SELECT `Data` FROM oneimagetest_wrong WHERE correct = 'N' 
) 
SELECT `crtuser` 
FROM oneimagetest 
WHERE oneimagetest.`Data` NOT IN ( 
	SELECT * FROM correct_table 
	) 
GROUP BY crtuser 
;
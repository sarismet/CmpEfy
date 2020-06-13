DELIMITER //
CREATE PROCEDURE SplitStr(IN Str VARCHAR(2000), IN Delim VARCHAR(1))  
    BEGIN
        DECLARE inipos INT;
        DECLARE endpos INT;
        DECLARE maxlen INT;
        DECLARE fullstr VARCHAR(2000);
        DECLARE item VARCHAR(2000);

        SET inipos = 1;
        SET fullstr = CONCAT(Str, delim);
        SET maxlen = LENGTH(fullstr);

        REPEAT
            SET endpos = LOCATE(delim, fullstr, inipos);
            SET item =  SUBSTR(fullstr, inipos, endpos - inipos);

            IF item <> '' AND item IS NOT NULL THEN           
                insert into rank_artists values(item);
            END IF;
            SET inipos = endpos + 1;
        UNTIL inipos >= maxlen END REPEAT;

	SELECT * from rank_artists;
    END//
DELIMITER ;


SELECT GROUP_CONCAT(asistantartist SEPARATOR ',') FROM Main where asistantartist <> 'no' GROUP BY 'all';






sql_procedure=""" CREATE PROCEDURE myprocedure(name TEXT,surname TEXT)
BEGIN
SELECT DISTINCT partner FROM 
(SELECT creator AS partner FROM Main WHERE Asistantartist = CONCAT(name,'_',surname) AND creator <> 'no' UNION ALL 
SELECT Asistantartist AS partner FROM Main WHERE creator = CONCAT(name,'_',surname) AND Asistantartist <> 'no' ) Main;
END;
"""




DELIMITER //
CREATE PROCEDURE curdemo(name TEXT,surname TEXT)
BEGIN
  DECLARE done INT DEFAULT FALSE;
  DECLARE a CHAR(100);
  DECLARE cur1 CURSOR FOR SELECT asistantartist FROM Main WHERE creator = CONCAT(name,'_',surname) AND asistantartist <> 'no';
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  OPEN cur1;


  read_loop: LOOP
    FETCH cur1 INTO a;
    IF done THEN
      LEAVE read_loop;
    END IF;
	call Splitforpartner(a);
  END LOOP;

  CLOSE cur1;
    insert into partners select creator from Main where asistantartist like CONCAT("%",name,'_',surname,"%");

select DISTINCT artistnames from partners;

END//

CREATE PROCEDURE Splitforrank(IN Str VARCHAR(200))  
    BEGIN
        DECLARE inipos INT;
        DECLARE endpos INT;
        DECLARE maxlen INT;
        DECLARE fullstr VARCHAR(2000);
        DECLARE item VARCHAR(2000);

        SET inipos = 1;
        SET fullstr = CONCAT(Str, ",");
        SET maxlen = LENGTH(fullstr);

        REPEAT
            SET endpos = LOCATE(",", fullstr, inipos);
            SET item =  SUBSTR(fullstr, inipos, endpos - inipos);

            IF item <> '' AND item IS NOT NULL THEN           
                insert into rank_artists values(item);
            END IF;
            SET inipos = endpos + 1;
        UNTIL inipos >= maxlen END REPEAT;

    END//
CREATE PROCEDURE Splitforpartner(IN Str VARCHAR(200))  
    BEGIN
        DECLARE inipos INT;
        DECLARE endpos INT;
        DECLARE maxlen INT;
        DECLARE fullstr VARCHAR(2000);
        DECLARE item VARCHAR(2000);

        SET inipos = 1;
        SET fullstr = CONCAT(Str, ",");
        SET maxlen = LENGTH(fullstr);

        REPEAT
            SET endpos = LOCATE(",", fullstr, inipos);
            SET item =  SUBSTR(fullstr, inipos, endpos - inipos);

            IF item <> '' AND item IS NOT NULL THEN           
                insert into partners values(item);
            END IF;
            SET inipos = endpos + 1;
        UNTIL inipos >= maxlen END REPEAT;

    END//
DELIMITER ;







DELIMITER //
CREATE TRIGGER likesongtrigger BEFORE UPDATE ON Songs
FOR EACH ROW BEGIN
IF( new.operation = 'like song' ) THEN
SET new.operation = 'NULL';
SET @listenerliked = (SELECT username FROM currentListener LIMIT 1);
INSERT INTO Main (wholiked,title,songid,albumid,creator,asistantartist)
SELECT * FROM (SELECT @listenerliked, new.title,new.id,new.albumid,new.creator,new.asistantartist) 
AS tmp WHERE NOT EXISTS (SELECT wholiked, songid FROM Main WHERE wholiked = @listenerliked and songid = new.id) LIMIT 1;
END IF;
END; //


CREATE TRIGGER likesalbumtrigger BEFORE UPDATE ON Songs
FOR EACH ROW BEGIN
IF( new.operation = 'like album' ) THEN
SET new.operation = 'NULL';
SET @listenerliked = (SELECT username FROM currentListener LIMIT 1);
INSERT INTO Main (wholiked,title,songid,albumid,creator,asistantartist)
SELECT * FROM (SELECT @listenerliked, new.title,new.id,new.albumid,new.creator,new.asistantartist) AS tmp WHERE NOT EXISTS (SELECT wholiked, songid FROM Main WHERE wholiked = @listenerliked and songid = new.id) LIMIT 1;
END IF;
END; //

CREATE TRIGGER deletesongtrigger BEFORE UPDATE ON Songs
FOR EACH ROW BEGIN
IF(new.operation = 'delete song' ) THEN
DELETE FROM Main Where songid = new.id;
END IF;
END; //
CREATE TRIGGER deletealbumtrigger BEFORE UPDATE ON Albums
FOR EACH ROW BEGIN
IF(new.operation = 'delete album' ) THEN
DELETE FROM Main WHERE albumid = new.id;
DELETE FROM Songs WHERE albumid = new.id;
END IF;
END; //


CREATE PROCEDURE curdemo(name TEXT,surname TEXT)
BEGIN
DECLARE done INT DEFAULT FALSE;
DECLARE a CHAR(200);
DECLARE cur1 CURSOR FOR SELECT asistantartist FROM Songs WHERE (creator = CONCAT(name,'_',surname) OR asistantartist like CONCAT("%",name,'_',surname,"%")) AND asistantartist <> 'no';
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


select DISTINCT artistnames from partners where artistnames <> CONCAT(name,'_',surname);

END; //

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

END; //
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

END; //
DELIMITER ;
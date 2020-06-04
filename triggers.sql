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
END;


CREATE TRIGGER deletesongtrigger BEFORE UPDATE ON Songs
FOR EACH ROW BEGIN
IF(new.operation = 'delete song' ) THEN
DELETE FROM Main Where songid = new.id;
END IF;
END;

CREATE TRIGGER deletealbumtrigger BEFORE UPDATE ON Albums
FOR EACH ROW BEGIN
IF(new.operation = 'delete album' ) THEN
DELETE FROM Main WHERE albumid = new.id;
DELETE FROM Songs WHERE albumid = new.id;
END IF;
END;

DELIMITER ;
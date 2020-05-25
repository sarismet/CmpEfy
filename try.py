"""import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="sarismet",
    database="Artist_Listener"
)
c = db.cursor()

guery = "insert into songs701 (idofsong) Select id From Songs where albumid = 701 ;"

c.execute(guery)

db.commit()
"""

sql_trigger = """CREATE TRIGGER Sour_trigger UPDATE OF likes ON Albums 
                    BEGIN
                        INSERT INTO {} (idofsongs) SELECT id FROM Songs Where albumid = {}
                        UPDATE Songs SET likes = (likes + 1) WHERE albumid = {};
                        UPDATE Artists SET likes = (likes + 1) WHERE name IN (SELECT creator From Songs Where albumid = {}) ;
                    END;""".format(1, 2, 3, 3)

print(sql_trigger)

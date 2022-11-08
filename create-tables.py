import pymysql

db_connection   = pymysql.connect( \
    host="benchmarksdb.cn5bfishmmmb.us-east-1.rds.amazonaws.com", 
    user="admin", password="vpcOwnChunkCloud", db="Ultron", port=3306, autocommit=True)

db_cursor = db_connection.cursor()

# erase dependent tables first.
db_cursor.execute( \
    """DROP TABLE IF EXISTS STTBenchmarks
    """)

db_cursor.execute( \
    """DROP TABLE IF EXISTS TTSBenchmarks
    """)

db_cursor.execute( \
    """DROP TABLE IF EXISTS Metrics""")

db_cursor.execute( \
    """DROP TABLE IF EXISTS STTServices
    """)

db_cursor.execute( \
    """DROP TABLE IF EXISTS TTSServices
    """)

db_cursor.execute( \
    """
    CREATE TABLE Metrics(metricId INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                         name VARCHAR(50) NOT NULL,
                         unit VARCHAR(50) NOT NULL)""")    
                               
db_cursor.execute( \
    """
    CREATE TABLE TTSServices(TTSServiceId INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                             name VARCHAR(50) NOT NULL)
    """
)

db_cursor.execute( \
    """
    CREATE TABLE STTServices(STTServiceId INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                             name VARCHAR(50) NOT NULL)
    """)

db_cursor.execute( \
    """
    CREATE TABLE STTBenchmarks(STTBenchmarkId INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                               metricId INT NOT NULL,
                               STTServiceId INT NOT NULL,
                               benchmarkValue FLOAT NOT NULL,
                               FOREIGN KEY (metricId)
                                   REFERENCES Metrics(metricId)
                                   ON UPDATE CASCADE ON DELETE RESTRICT,
                               FOREIGN KEY (STTServiceId)
                                   REFERENCES STTServices(STTServiceId)
                                   ON UPDATE CASCADE ON DELETE RESTRICT)
                                  
    """)

db_cursor.execute( \
    """
    CREATE TABLE TTSBenchmarks(TTSBenchmarkId INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                               metricId INT NOT NULL,
                               TTSServiceId INT NOT NULL,
                               benchmarkValue FLOAT NOT NULL,
                               FOREIGN KEY (metricId)
                                   REFERENCES Metrics(metricId)
                                   ON UPDATE CASCADE ON DELETE RESTRICT,
                               FOREIGN KEY (TTSServiceId)
                                   REFERENCES TTSServices(TTSServiceId)
                                   ON UPDATE CASCADE ON DELETE RESTRICT)                             
    
    """)

print("voy a insertar xd")

db_cursor.execute( \
    """
    INSERT INTO Metrics (name, unit) VALUES ("latencia", "ms");
    """)

db_cursor.execute( \
    """
    INSERT INTO Metrics (name, unit) VALUES ("Exactitud", "Porcentaje")
    """)

db_cursor.execute( \
    """
    INSERT INTO STTServices (name) VALUES ("Transcribe")
    """)

db_cursor.execute( \
    """
    INSERT INTO STTServices (name) VALUES ("Azure")
    """)

db_cursor.execute( \
    """
    INSERT INTO TTSServices (name) VALUES ("Polly")
    """)

db_cursor.execute( \
    """
    INSERT INTO STTServices (name) VALUES ("Google")
    """)

db_cursor.execute( \
    """
    INSERT INTO STTBenchmarks (metricId, STTServiceId, benchmarkValue) 
    VALUES ((SELECT metricId FROM Metrics WHERE name = "Latencia"), 
            (SELECT STTServiceId FROM STTServices WHERE name = "Transcribe"), 
            10000)
    """)

db_cursor.execute( \
    """
    INSERT INTO STTBenchmarks (metricId, STTServiceId, benchmarkValue) 
    VALUES ((SELECT metricId FROM Metrics WHERE name = "Latencia"), 
            (SELECT STTServiceId FROM STTServices WHERE name = "Transcribe"), 
            5000)
    """)

db_cursor.execute( \
    """
    INSERT INTO STTBenchmarks (metricId, STTServiceId, benchmarkValue) 
    VALUES ((SELECT metricId FROM Metrics WHERE name = "Exactitud"), 
            (SELECT STTServiceId FROM STTServices WHERE name = "Transcribe"), 
            10000)
    """)

db_cursor.execute( \
    """select s.name, avg(benchmarkValue) 
    from Metrics as m, STTBenchmarks as b, STTServices as s 
    where m.metricId = b.metricId and s.STTServiceId = b.STTServiceId and m.name = "Latencia" 
    group by s.name""")

rows = db_cursor.fetchall()
for row in rows:
    print(row)


# intermediate table after parent tables so that references exist.
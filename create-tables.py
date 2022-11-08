# import the mysql client for python
import pymysql

db_connection   = pymysql.connect( \
    host="benchmarksdb.cn5bfishmmmb.us-east-1.rds.amazonaws.com", 
    user="admin", password="vpcOwnChunkCloud", db="Ultron")

db_cursor = db_connection.cursor()

db_cursor.execute( \
    """IF OBJECT_ID('dbo.Metrics', 'U') IS NOT NULL DROP TABLE dbo.Metrics;""")

db_cursor.execute( \
    """IF OBJECT_ID('dbo.STTServices', 'U') IS NOT NULL 
       DROP TABLE dbo.STTServices; 
    """)

db_cursor.execute( \
    """IF OBJECT_ID('dbo.TTSServices', 'U') IS NOT NULL 
       DROP TABLE dbo.TTSServices; 
    """)

db_cursor.execute( \
    """IF OBJECT_ID('dbo.STTBenchmarks', 'U') IS NOT NULL 
       DROP TABLE dbo.STTBenchmarks; 
    """)

db_cursor.execute( \
    """IF OBJECT_ID('dbo.TTSBenchmarks', 'U') IS NOT NULL 
       DROP TABLE dbo.TTSBenchmarks; 
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
                                   ON UPDATE CASCADE ON DELETE RESTRICT,
                               )
                                  
    """)

db_cursor.execute(
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
                                   ON UPDATE CASCADE ON DELETE RESTRICT,
                               )                             
    
    """)




# intermediate table after parent tables so that references exist.
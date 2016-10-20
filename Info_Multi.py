import MySQLdb

conn = MySQLdb.connect (host = "localhost",    #inserire host (localhost)
                           user = "root",      #user mysql
                           passwd = "ale1992", #password mysql 
                           db = "InformaticaMultimediale")  #nome dv
#crea connessione
cursor = conn.cursor()

#esegue select dal db leggendo i dati della tabella AOI
cursor.execute ("SELECT * FROM AOI")

#salva il risultato della query nella lista
AOI=cursor.fetchall()


cursor.execute("SELECT * FROM DB")

db= cursor.fetchall()
cursor.execute ("CREATE TABLE IF NOT EXISTS USER_IN (id VARCHAR(100),timestamp TIMESTAMP,x DECIMAL(4,2), y DECIMAL(4,2));")
cursor.execute ("CREATE TABLE IF NOT EXISTS USER_OUT (id VARCHAR(100),timestamp TIMESTAMP,x DECIMAL(4,2), y DECIMAL(4,2));")


#dichiaro due indici per ogni tabella del database, poi confronto i parametri
for i in db:
	    a=False
            for m in AOI:
                
                if i[2] < m[3] and i[2] > m[1] and i[3] < m[4] and i[3] > m[2]: #valuto se l'osservatore guarda all'interno dell'AOI
                  a=True
                  print "La persona",i[0],"sta osservando il punto d'interesse",m[0]
                  cursor.execute("INSERT INTO USER_IN (id,timestamp,x,y) VALUES(%s,%s,%s,%s)", (i[0],i[1],i[2],i[3])) 
                  conn.commit()
            if a==False:
                print "La persona",i[0],"non sta osservando alcun punto d'interesse" #valuto se l'osservatore guarda al di fuori dell'AOI
                cursor.execute("INSERT INTO USER_OUT (id,timestamp,x,y) VALUES(%s,%s,%s,%s)", (i[0],i[1],i[2],i[3]))     
                conn.commit()            
                  
                   

cursor.close()
conn.close()

      
      








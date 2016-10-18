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

cursor.close()
conn.close()

#dichiaro due indici per ogni tabella del database, poi confronto i parametri
for i in db:
            for m in AOI:
                if i[2] < m[3] and i[2] > m[1] and i[3] < m[4] and i[3] > m[2]: #valuto se l'osservatore guarda all'interno dell'AOI

                   print "La persona",i[0],"sta osservando il punto d'interesse",m[0]
                   
                   

                   








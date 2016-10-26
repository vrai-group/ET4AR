import sys
from decimal import *
getcontext().prec = 3 #Precisione del decimale
from datetime import datetime
import MySQLdb

try:
    conn = MySQLdb.connect(host = "localhost", user = "root", passwd="", db="eye_tracking")

    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS user_in (id_user VARCHAR(15), timestamp TIMESTAMP NULL DEFAULT NULL, x DECIMAL(4,2), y DECIMAL(4,2), aoi INT(2));")
    cursor.execute("SELECT * FROM user_in;")
    num_user_in = cursor.rowcount

    cursor.execute("CREATE TABLE IF NOT EXISTS user_out (id_user VARCHAR(15), timestamp TIMESTAMP NULL DEFAULT NULL, x DECIMAL(4,2), y DECIMAL(4,2), near_aoi INT(2));")
    cursor.execute("SELECT * FROM user_out;")
    num_user_out = cursor.rowcount

    cursor.execute("CREATE TABLE IF NOT EXISTS saccades (id_row INT NOT NULL AUTO_INCREMENT PRIMARY KEY, id_user VARCHAR(15), saccade INT(2), aoi INT(2));")

    itera = True #permette di far ricomparire a video il menu, ad ogni termine di operazione
    while itera:
        menu = input('\nDigita:\n 1 - Per dividere gli utenti che guardano in una AOI da quelli che guardano all\'esterno;\n 2 - Per visualizzare gli sguardi all\'interno di una specifica AOI;\n 3 - Per visualizzare gli utenti che guardano all\'esterno delle AOI;\n 4 - Per calcolare l\'aoi piu\' vicina ad ogni sguardo esterno;\n 5 - Per visualizzare il movimento dello sguardo di un utente;\n 6 - Per calcolare la matrice di emissione;\n 0 - Per uscire dal programma.\n')
        if menu == 1:
           if num_user_in == 0 and num_user_out == 0: #Se le tabelle user_in e user_out sono vuote, allora
              cursor.execute("SELECT * FROM aoi;")
              aoi = cursor.fetchall()

              cursor.execute("SELECT * FROM db;")
              num_row_db = cursor.rowcount
              db = cursor.fetchall()
       
              for i in db:
                  print "...ATTENDERE... Righe da processare: ", num_row_db #visualizza l'avanzamento del processo in termini di countdown delle righe mancanti
                  a = False #flag che permette il funzionamento
                  for m in aoi:
                      if i[2] < m[3] and i[2] > m[1] and i[3] < m[4] and i[3] > m[2]: #valuto se l'osservatore guarda all'interno dell'AOI
                         a = True
                         cursor.execute("INSERT INTO user_in (id_user, timestamp, x, y, aoi) VALUES (%s, %s, %s, %s, %s)", (i[0], i[1], i[2], i[3], m[0])) 
                         conn.commit()
                         num_row_db = num_row_db - 1 #sottraggo una riga al conto totale delle righe
                  if a == False: #se l'osservatore non guarda all'interno di alcuna AOI, allora
                     cursor.execute("INSERT INTO user_out (id_user, timestamp, x, y) VALUES (%s, %s, %s, %s)", (i[0], i[1], i[2], i[3]))     
                     conn.commit()
                     num_row_db = num_row_db - 1 #sottraggo una riga al conto totale delle righe
              print "Utenti divisi."
           else: #se le tabelle user_in e user_out non sono vuote, allora
              print "Utenti gia' divisi."
        elif menu == 2:
             cursor.execute("SELECT id_user, timestamp, x, y FROM user_in;")
             num_user_in = cursor.rowcount
             if num_user_in == 0: #Rende necessario svolgere prima il comando 1
                print "\nImpossibile visualizzare gli utenti se non sono stati prima divisi.\n Selezionare l'opzione 1"
             else:
                print "Selezionare un'area di interesse\n"
                cursor.execute("SELECT num FROM aoi")
                aoi_number = cursor.rowcount
                aoi_id = cursor.fetchall()
                aoi_list = []
                print "Areas Of Interest:\n"
                for aoi in aoi_id:
                    aoi_list.append(aoi)
                for i in range(1, aoi_number + 1):
                    print "  ", i
                aoi_selector = input()
                if aoi_selector > 0 and aoi_selector <= aoi_number:
                   cursor.execute("SELECT id_user, timestamp, x, y FROM user_in WHERE aoi = %s", aoi_list[aoi_selector - 1])
                   user_in = cursor.fetchall()
                   user_in_num = cursor.rowcount
                   if user_in_num == 0:
                      print "Nessun utente guarda all\'interno dell\'aoi", aoi_selector
                   else:
                      for row in user_in:
                          print row
        elif menu == 3:
             cursor.execute("SELECT * FROM user_out;")
             num_user_out = cursor.rowcount
             if num_user_out == 0: #Rende necessario svolgere prima il comando 1
                print "\nImpossibile visualizzare gli utenti se non sono stati prima divisi.\n Selezionare l'opzione 1"
             else:
                print "Selezionare un'area di interesse\n"
                cursor.execute("SELECT num FROM aoi")
                aoi_number = cursor.rowcount
                aoi_id = cursor.fetchall()
                near_aoi_list = []
                print "Areas Of Interest:\n"
                for aoi in aoi_id:
                    near_aoi_list.append(aoi)
                for i in range(1, aoi_number + 1):
                    print "  ", i
                near_aoi_selector = input()
                if near_aoi_selector > 0 and near_aoi_selector <= aoi_number:
                   cursor.execute("SELECT id_user, timestamp, x, y FROM user_out WHERE near_aoi = %s", near_aoi_list[near_aoi_selector - 1])
                   user_out = cursor.fetchall()
                   user_out_num = cursor.rowcount
                   if user_out_num == 0:
                      print "Nessun utente guarda nei dintorni dell\'aoi", near_aoi_selector
                   else:
                      for row in user_out:
                          print row
        elif menu == 4:
             cursor.execute("SELECT * FROM user_out WHERE near_aoi IS NULL")
             num_near_null = cursor.rowcount #conta il numero di righe con attributo near_aoi pari al valore di default, null
             if num_near_null != 0: #se qualche attributo near_aoi ha valore di default, allora
                cursor.execute("SELECT * FROM user_out;")
                num_user_out = cursor.rowcount
                user_out = cursor.fetchall()

                cursor.execute("SELECT * FROM aoi;")
                aoi = cursor.fetchall()
                for i in user_out:
                    print "...ATTENDERE... Righe da processare: ", num_user_out
                    min_x_absl = 45 #inizializzo a valore massimo delle x
                    min_y_absl = 35 #inizializzo a valore massimo delle y
                    min_x = 0
                    min_y = 0
                    near_aoi = 0
                    for n in aoi:
                        if i[2] > n[1]: #questo blocco if-else serve per non far venire il risultato negativo
                           count = i[2] - n[1]
                        else:
                           count = n[1] - i[2]

                        min_x = count

                        if i[2] > n[3]: #questo blocco if-else serve per non far venire il risultato negativo
                           count = i[2] - n[3]
                        else:
                           count = n[3] - i[2]

                        if count < min_x: #se count ha valore minore a min_x, allora
                           min_x = count

                        if i[3] > n[2]: #questo blocco if-else serve per non far venire il risultato negativo
                           count = i[3] - n[2]
                        else:
                           count = n[2] - i[3]

                        min_y = count

                        if i[3] > n[4]: #questo blocco if-else serve per non far venire il risultato negativo
                           count = i[3] - n[4]
                        else:
                           count = n[4] - i[3]

                        if count < min_y: #se count ha valore minore a min_y, allora
                           min_y = count

                        if min_x < min_x_absl and min_y < min_y_absl: #se min_x e min_y sono minori rispettivamente di min_x_absl e min_y_absl, allora
                           min_x_absl = min_x #assegna i valori di min_x e min_y a min_x_absl e min_y_absl
                           min_y_absl = min_y
                           near_aoi = n[0] #e definisci l'AOI corrente come AOI piu' vicina

                    cursor.execute("UPDATE user_out SET near_aoi = %s WHERE id_user = %s and timestamp = %s and x = %s and y = %s;", (near_aoi, i[0], i[1], i[2], i[3]))
                    conn.commit()
                    num_user_out = num_user_out - 1 #sottraggo una riga al conto totale delle righe
             else: #Se non vi sono attributi near_aoi pari a null, allora 
                cursor.execute("SELECT * FROM user_out")
                num_user_out = cursor.rowcount
                if num_user_out == 0: #se il numero delle righe della tabella user_out e' pari a zero, allora
                   print "\nImpossibile calcolare AOI piu\' vicina, se prima non sono stati divisi gli utenti che guardano all'esterno o all'interno di una AOI.\n Selezionare l'opzione 1"
                else: #se il numero delle righe della tabella user_out e' diverso da zero, vuol dire che il calcolo alle AOI piu' vicine e' gia stato effettuato
                   print "Vicinanza AOI gia\' calcolata."
        elif menu == 5:
             cursor.execute("SELECT * FROM user_out WHERE near_aoi IS NULL")
             near_aoi_is_null = cursor.rowcount
             if near_aoi_is_null != 0: # Se esistono righe con aoi nulla allora bisogna calcolare le aoi piu' vicine (opzione 4)
                print "Impossibile eseguire il comando se prima non si calcolano le AOI piu\' vicina agli sguardi esterni.\n Selezionare l'opzione 4"
             else: # Altrimenti
                iter = True
                while iter: # Per iterare il sottomenu
                    print "Selezionare l\'utente di cui si vuole visualizzare il movimento dello sguardo:"
                    print "  0  -  Tutti"
                    id_list = ['Tutti']
                    cursor.execute("SELECT DISTINCT id_user FROM db")
                    id_distinct = cursor.fetchall() # Gli utenti nel db
                    num_id_distinct = cursor.rowcount
                    id_num = 0
                    for id in id_distinct:
                        id_num = id_num + 1
                        print " ", id_num, " - ", id
                        id_list.append(id) # Aggiunge alla lista tutti gli utenti presenti nel db e li visualizza
                    id_selector = input() # Input utente
                    if id_selector < num_id_distinct + 1 and id_selector != 0: # Se il numero immesso e' inferiore al numero massimo di utenti e diverso da 0, allora
                       cursor.execute("SELECT * FROM saccades WHERE id_user = %s", id_list[id_selector])
                       num_saccade_for_user = cursor.rowcount
                       if num_saccade_for_user == 0:
                          cursor.execute("SELECT * FROM db WHERE id_user = %s ORDER BY timestamp ASC", id_list[id_selector])
                          dot_id = cursor.fetchall() # Visualizza le righe dalla tabella \'db\' dove id_user e' uguale a quello selezionato dall\'utente. In ordine di tempo, dal piu' vecchio al piu' nuovo
                          num_dot = cursor.rowcount
                          aoi_list = []
                          aoi_list_intermedia = []
                          app =  dot_id[0]
                          appoggio = app[1]
                          for dot in dot_id:
                              cursor.execute("SELECT aoi FROM user_in WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (dot[0], dot[1], dot[2], dot[3]))
                              aoi_user_in = cursor.fetchall()
                              num_aoi_user_in = cursor.rowcount
                              if num_aoi_user_in != 0:
                                 print "in ", id_list[id_selector], " utente numero: ", id_selector, " ...ATTENDERE... Righe da processare: ", num_dot
                                 timestamp1 = str(dot[1])
                                 timestamp2 = str(appoggio)
                                 t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                                 t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                                 difference = t1-t2
                                 if (difference.seconds)<30:
                                    aoi_list_intermedia.append(aoi_user_in)
                                 else:
                                    aoi_list.append(aoi_list_intermedia)
                                    aoi_list_intermedia=[]
                                    aoi_list_intermedia.append(aoi_user_in)
                              else:
                                 cursor.execute("SELECT near_aoi FROM user_out WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (dot[0], dot[1], dot[2], dot[3]))
                                 aoi_user_out = cursor.fetchall()
                                 print "out ", id_list[id_selector], " utente numero: ", id_selector, " ...ATTENDERE... Righe da processare: ", num_dot
                                 timestamp1 = str(dot[1])
                                 timestamp2 = str(appoggio)
                                 t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                                 t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                                 difference = t1-t2
                                 if (difference.seconds)<30:
                                    aoi_list_intermedia.append(aoi_user_out)
                                 else:
                                    aoi_list.append(aoi_list_intermedia)
                                    aoi_list_intermedia=[]
                                    aoi_list_intermedia.append(aoi_user_out)
                              num_dot = num_dot - 1
                              appoggio = dot[1]
                          aoi_list.append(aoi_list_intermedia)
                          num_saccade = -1
                          for saccade in aoi_list:
                                print "SACCADE NUMERO ", num_saccade
                                num_saccade = num_saccade + 1
                                num_aoi = -1
                                for aoi_sacc in saccade:
                                      num_aoi = num_aoi + 1
                                      print num_aoi, " --- AOI NUMERO ", aoi_list[num_saccade][num_aoi]
                                      cursor.execute("INSERT INTO saccades (id_user, saccade, aoi) VALUES (%s, %s, %s)", (id_list[id_selector], num_saccade, aoi_list[num_saccade][num_aoi]))
                                      conn.commit()
                       else:
                          cursor.execute("SELECT * FROM saccades WHERE id_user = %s ORDER BY id_row ASC", id_list[id_selector])
                          saccade_for_user = cursor.fetchall()
                          for saccade in saccade_for_user:
                              print "Sguardo numero: ", saccade[2], " - Verso l'aoi: ", saccade[3]
                       iter = False                       
                    elif id_selector == 0:
                       id_list_len = len(id_list)
                       for num in range(1,id_list_len):
                           cursor.execute("SELECT * FROM saccades WHERE id_user = %s", id_list[num])
                           num_saccade_for_user = cursor.rowcount
                           if num_saccade_for_user == 0:
                              cursor.execute("SELECT * FROM db WHERE id_user = %s ORDER BY timestamp ASC", id_list[num])
                              dot_id = cursor.fetchall()
                              num_dot = cursor.rowcount
                              aoi_list = []
                              aoi_list_intermedia = []
                              app =  dot_id[0]
                              appoggio = app[1]
                              for dot in dot_id:
                                  cursor.execute("SELECT aoi FROM user_in WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (dot[0], dot[1], dot[2], dot[3]))
                                  aoi_user_in = cursor.fetchall()
                                  num_aoi_user_in = cursor.rowcount
                                  if num_aoi_user_in != 0:
                                     print "in ", id_list[num], " utente numero: ", num, " ...ATTENDERE... Righe da processare: ", num_dot
                                     timestamp1 = str(dot[1])
                                     timestamp2 = str(appoggio)
                                     t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                                     t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                                     difference = t1-t2
                                     if (difference.seconds)<30:
                                        aoi_list_intermedia.append(aoi_user_in)
                                     else:
                                        aoi_list.append(aoi_list_intermedia)
                                        aoi_list_intermedia=[]
                                        aoi_list_intermedia.append(aoi_user_in)
                                  else:
                                     cursor.execute("SELECT near_aoi FROM user_out WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (dot[0], dot[1], dot[2], dot[3]))
                                     aoi_user_out = cursor.fetchall()
                                     print "out ", id_list[num], " utente numero: ", num, " ...ATTENDERE... Righe da processare: ", num_dot
                                     timestamp1 = str(dot[1])
                                     timestamp2 = str(appoggio)
                                     t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                                     t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                                     difference = t1-t2
                                     if (difference.seconds)<30:
                                        aoi_list_intermedia.append(aoi_user_out)
                                     else:
                                        aoi_list.append(aoi_list_intermedia)
                                        aoi_list_intermedia=[]
                                        aoi_list_intermedia.append(aoi_user_out)
                                  num_dot = num_dot - 1
                                  appoggio = dot[1]
                              aoi_list.append(aoi_list_intermedia)
                              num_saccade = -1
                              for saccade in aoi_list:
                                  print "SACCADE NUMERO ", num_saccade
                                  num_saccade = num_saccade + 1
                                  num_aoi = -1
                                  for aoi_sacc in saccade:
                                      num_aoi = num_aoi + 1
                                      print num_aoi, " --- AOI NUMERO ", aoi_list[num_saccade][num_aoi]
                                      cursor.execute("INSERT INTO saccades (id_user, saccade, aoi) VALUES (%s, %s, %s)", (id_list[num], num_saccade, aoi_list[num_saccade][num_aoi]))
                                      conn.commit()
                           else:
                              cursor.execute("SELECT * FROM saccades WHERE id_user = %s ORDER BY id_row ASC", id_list[num])
                              saccade_for_user = cursor.fetchall()
                              for saccade in saccade_for_user:
                                  print "Sguardo numero: ", saccade[2], " - Verso l'aoi: ", saccade[3]
                       iter = False
                    else:
                       print "Numero non valido"
        elif menu == 6:
             cursor.execute("SELECT num FROM aoi")
             aoi_number = cursor.rowcount
             cursor.execute("SELECT DISTINCT id_user FROM db")
             id_distinct = cursor.fetchall()
             num_id_distinct = cursor.rowcount
             m=[]
             u=0
             for i in range(1, aoi_number + 1):
                mat=[]
                coeff=0
                for id in id_distinct:
                    cursor.execute("SELECT * FROM user_in WHERE id_user = %s AND aoi = %s;", (id[0], i))
                    num_user_in = cursor.rowcount
                    cursor.execute("SELECT * FROM user_out WHERE id_user = %s AND near_aoi = %s;", (id[0], i))
                    num_user_out = cursor.rowcount
                    totale = num_user_in + num_user_out
                    mat.append(totale)
                    print "L'utente",id[0],"guarda direttamente o in prossimita dell'aoi", i, "per", totale, "volte"
                    coeff = coeff + totale
                for n in range(0, num_id_distinct):
                    mat[n] = Decimal(mat[n]) / Decimal(coeff)
                m.append(mat)
             print m
        elif menu == 0: #per uscire dal programma
             print "Arrivederci!"
             itera = False
        else:
	        print "Hai digitato un numero non consentito."

except MySQLdb.Error, e: #Printa l'errore in caso di presenza dello stesso
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally: #infine si chiude la connessione
    if conn:
	   conn.close()
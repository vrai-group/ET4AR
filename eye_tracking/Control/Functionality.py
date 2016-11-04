'''
Created on 28 ott 2016

@author: simon
'''
from datetime import datetime
from decimal import *
getcontext().prec = 3 #Precisione del decimale

from Model.Database import *

import numpy as np
import matplotlib.pyplot as plt

from hmmlearn import hmm

'''
divUsers(cursor)

Divide le fixations in fix_in (dentro le aoi) e fix_out (fuori le aoi; nell'aoi complementare)
Ad ogni fix_in associa l'aoi corrispondente 
'''
def divFix(conn, cursor):
    num_fix_in = countRowTable(cursor, 'fix_in')
    num_fix_out = countRowTable(cursor, 'fix_out')
    if num_fix_in == 0 and num_fix_out == 0: #Se le tabelle user_in e user_out sono vuote, allora
        aoi = selectFromTable(cursor, 'aoi')
        db = selectFromTable(cursor, 'db')
        num_db = countRowTable(cursor, 'db')
        for i in db:
            print "...ATTENDERE... Righe da processare: ", num_db #visualizza l'avanzamento del processo in termini di countdown delle righe mancanti
            a = False #flag che permette il funzionamento
            for m in aoi:
                if i[2] <= m[3] and i[2] >= m[1] and i[3] <= m[4] and i[3] >= m[2]: #valuto se l'osservatore guarda all'interno dell'AOI
                    a = True
                    insertToTable(conn, cursor, 'fix_in', i[0], i[1], i[2], i[3], 'NULL')
            if a == False: #se l'osservatore non guarda all'interno di alcuna AOI, allora
                insertToTable(conn, cursor, 'fix_out', i[0], i[1], i[2], i[3], 'NULL')
            num_db = num_db - 1 #sottraggo una riga al conto totale delle righe
        delDuplicatiFixIn(conn, cursor)
        print "Fixations divise."
    else: #se le tabelle user_in e user_out non sono vuote, allora
        print "Fixations gia' divise."

def delDuplicatiFixIn(conn, cursor):
    row_distinct = selectFromTable(cursor, 'fix_in DISTINCT')
    count_row_distinct = countRowTable(cursor, 'fix_in DISTINCT')
    truncTable(cursor, 'fix_in')
    for rowDist in row_distinct:
        print count_row_distinct, " ...OTTIMIZZAZIONE... Inserimento riga", rowDist
        insertToTable(conn, cursor, 'fix_in', rowDist[0], rowDist[1], rowDist[2], rowDist[3], 'NULL')
        count_row_distinct = count_row_distinct - 1

def printListAoi(cursor):
    aoi_count = countRowTable(cursor, 'aoi')
    for i in range(1, aoi_count + 1):
        print "  ", i

def fixInAoi(conn, cursor):
    fix_count = countRowTable(cursor, 'fix_in')
    if fix_count == 0:
        print "\nImpossibile visualizzare le fixations se prima non sono state divise.\n Selezionare l'opzione 1"
    else:
        printListAoi(cursor)
        aoi_selector = input()
        if aoi_selector > 0 and aoi_selector <= countRowTable(cursor, 'aoi'):
            fix_in_aoi = selectFromTableWhere(conn, cursor, 'fix_in', 'aoi', str(aoi_selector))
            count_fix_in_aoi = countRowTableWhere(conn, cursor, 'fix_in', 'aoi', str(aoi_selector), 'NULL', 'NULL')
            if count_fix_in_aoi == 0:
                print "Nessun utente guarda all\'interno dell\'aoi", aoi_selector
            else:
                count = 0
                for row in fix_in_aoi:
                    print row
                    count = count + 1
                print count, "fixations nell\'AOI", aoi_selector

def fixOutAoi(conn, cursor):
    fix_count = countRowTable(cursor, 'fix_out')
    if fix_count == 0:
        print "\nImpossibile visualizzare le fixations se prima non sono state divise.\n Selezionare l'opzione 1"
    else:
        printListAoi(cursor)
        near_aoi_selector = input()
        if near_aoi_selector > 0 and near_aoi_selector <= countRowTable(cursor, 'aoi'):
            fix_out_aoi = selectFromTableWhere(conn, cursor, 'fix_out', 'near_aoi', str(near_aoi_selector))
            count_fix_out_aoi = countRowTableWhere(conn, cursor, 'fix_out', 'near_aoi', str(near_aoi_selector), 'NULL', 'NULL')
            if count_fix_out_aoi == 0:
                print "Nessun utente guarda all\'interno dell\'aoi", near_aoi_selector
            else:
                count = 0
                for row in fix_out_aoi:
                    print row
                    count = count + 1
                print count, "fixations vicino l\'AOI", near_aoi_selector

def aoiFixIn(conn, cursor):
    aoi_count_null = countRowTableWhere(conn, cursor, 'fix_in', 'aoi', 'IS NULL', 'NULL', 'NULL')
    if aoi_count_null != 0: #Se le tabelle user_in e user_out sono vuote, allora
        aoi = selectFromTable(cursor, 'aoi')
        fix_in = selectFromTable(cursor, 'fix_in')
        num_fix_in = countRowTable(cursor, 'fix_in')
        for i in fix_in:
            print "...ATTENDERE... Righe da processare: ", num_fix_in #visualizza l'avanzamento del processo in termini di countdown delle righe mancanti
            for m in aoi:
                if i[2] <= m[3] and i[2] >= m[1] and i[3] <= m[4] and i[3] >= m[2]: #valuto se l'osservatore guarda all'interno dell'AOI
                    updateTable(conn, cursor, 'fix_in', m[0], i[0], i[1], i[2], i[3])
            num_fix_in = num_fix_in - 1
    else:
        num_fix_in = countRowTable(cursor, 'fix_in')
        if num_fix_in == 0: #se il numero delle righe della tabella user_out e' pari a zero, allora
            print "\nImpossibile calcolare AOI osservata, se prima non sono stati divisi gli utenti che guardano all'esterno o all'interno di una AOI.\n Selezionare l'opzione 1"
        else: #se il numero delle righe della tabella fix_out e' diverso da zero, vuol dire che il calcolo alle AOI piu' vicine e' gia stato effettuato
            print "AOI gia\' calcolata."

def nearAoiFixOut(conn, cursor):
    near_aoi_count_null = countRowTableWhere(conn, cursor, 'fix_out', 'near_aoi', 'IS NULL', 'NULL', 'NULL')
    if near_aoi_count_null != 0:
        fix_out = selectFromTable(cursor, 'fix_out')
        count_fix_out = countRowTable(cursor, 'fix_out')
        aoi = selectFromTable(cursor, 'aoi')
        for i in fix_out:
            print "...ATTENDERE... Righe da processare: ", count_fix_out
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

            updateTable(conn, cursor, 'fix_out', near_aoi, i[0], i[1], i[2], i[3])
            count_fix_out = count_fix_out - 1 #sottraggo una riga al conto totale delle righe
    else: #Se non vi sono attributi near_aoi pari a null, allora 
        num_fix_out = countRowTable(cursor, 'fix_out')
        if num_fix_out == 0: #se il numero delle righe della tabella user_out e' pari a zero, allora
            print "\nImpossibile calcolare AOI piu\' vicina, se prima non sono stati divisi gli utenti che guardano all'esterno o all'interno di una AOI.\n Selezionare l'opzione 1"
        else: #se il numero delle righe della tabella fix_out e' diverso da zero, vuol dire che il calcolo alle AOI piu' vicine e' gia stato effettuato
            print "Vicinanza AOI gia\' calcolata."

def printListUsers(cursor):
    print "Selezionare l\'utente:"
    print "  0  -  Tutti"
    id_list = ['Tutti']
    cursor.execute("SELECT DISTINCT id_user FROM db")
    id_distinct = cursor.fetchall() # Gli utenti nel db
    id_num = 0
    for id in id_distinct:
        id_num = id_num + 1
        print " ", id_num, " - ", id
        id_list.append(id) # Aggiunge alla lista tutti gli utenti presenti nel db e li visualizza
    return id_list

def viewSaccadesOfUser(conn, cursor):
    count_near_aoi_isnull = countRowTableWhere(conn, cursor, 'fix_out', 'near_aoi', 'IS NULL', 'NULL', 'NULL')
    if count_near_aoi_isnull != 0: # Se esistono righe con aoi nulla allora bisogna calcolare le aoi piu' vicine (opzione 4)
        print "Impossibile eseguire il comando se prima non si calcolano le AOI piu\' vicine alle fixations esterne.\n Selezionare l'opzione 5"
    else:
        iter = True
        while iter:
            id_list = printListUsers(cursor)
            num_id_distinct = len(id_list)
            id_selector = input()
            if id_selector < num_id_distinct + 1 and id_selector != 0:
                num_saccades_for_user = countRowTableWhere(conn, cursor, 'saccades', 'id_user', id_list[id_selector], 'NULL', 'NULL')
                if num_saccades_for_user == 0:
                    fix_id = selectFromTableWhere(conn, cursor, 'db', 'id_user order by timestamp', id_list[id_selector])
                    fix_count = countRowTableWhere(conn, cursor, 'db', 'id_user order by timestamp', id_list[id_selector], 'NULL', 'NULL')
                    aoi_list = []
                    aoi_list_intermedia = []
                    app =  fix_id[0]
                    appoggio = app[1]
                    for fix in fix_id:
                        sel_aoi = selectAoiOrNearAoi(conn, cursor, 'fix_in', fix[0], fix[1], fix[2], fix[3])
                        count_aoi = countAoiOrNearAoi(conn, cursor, 'fix_in', fix[0], fix[1], fix[2], fix[3])
                        if count_aoi != 0:
                            print "in ", id_list[id_selector], " utente numero: ", id_selector, " ...ATTENDERE... Righe da processare: ", fix_count
                            timestamp1 = str(fix[1])
                            timestamp2 = str(appoggio)
                            t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                            t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                            difference = t1 - t2
                            if (difference.seconds) < 30:
                                aoi_list_intermedia.append(sel_aoi)
                            else:
                                aoi_list.append(aoi_list_intermedia)
                                aoi_list_intermedia = []
                                aoi_list_intermedia.append(sel_aoi)
                        else:
                            sel_near_aoi = selectAoiOrNearAoi(conn, cursor, 'fix_out', fix[0], fix[1], fix[2], fix[3])
                            print "out ", id_list[id_selector], " utente numero: ", id_selector, " ...ATTENDERE... Righe da processare: ", fix_count
                            timestamp1 = str(fix[1])
                            timestamp2 = str(appoggio)
                            t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                            t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                            difference = t1 - t2
                            if (difference.seconds) < 30:
                                aoi_list_intermedia.append(sel_near_aoi)
                            else:
                                aoi_list.append(aoi_list_intermedia)
                                aoi_list_intermedia = []
                                aoi_list_intermedia.append(sel_near_aoi)
                        fix_count = fix_count - 1
                        appoggio = fix[1]
                    aoi_list.append(aoi_list_intermedia)
                    num_saccade = -1
                    for saccade in aoi_list:
                        num_saccade = num_saccade + 1
                        print "SACCADE NUMERO ", num_saccade
                        num_aoi = -1
                        for aoi_sacc in saccade:
                            num_aoi = num_aoi + 1
                            print num_aoi, " --- AOI NUMERO ", aoi_list[num_saccade][num_aoi]
                            insertToTable(conn, cursor, 'saccades', id_list[id_selector], num_saccade, aoi_list[num_saccade][num_aoi], 'NULL', 'NULL')
                else:
                    saccade_for_user = selectFromTableWhere(conn, cursor, 'saccades', 'id_user order by id_row', id_list[id_selector])
                    for saccade in saccade_for_user:
                        print "Sguardo numero: ", saccade[2], " - Verso l'aoi: ", saccade[3]
                iter = False
            elif id_selector == 0:
                for num in range(1, num_id_distinct):
                    num_saccade_for_user = countRowTableWhere(conn, cursor, 'saccades', 'id_user', id_list[num], 'NULL', 'NULL')
                    if num_saccade_for_user == 0:
                        fix_id = selectFromTableWhere(conn, cursor, 'db', 'id_user order by timestamp', id_list[num])
                        fix_count = countRowTableWhere(conn, cursor, 'db', 'id_user order by timestamp', id_list[num], 'NULL', 'NULL')
                        aoi_list = []
                        aoi_list_intermedia = []
                        app =  fix_id[0]
                        appoggio = app[1]
                        for fix in fix_id:
                            sel_aoi = selectAoiOrNearAoi(conn, cursor, 'fix_in', fix[0], fix[1], fix[2], fix[3])
                            count_aoi = countAoiOrNearAoi(conn, cursor, 'fix_in', fix[0], fix[1], fix[2], fix[3])
                            if count_aoi != 0:
                                print "in ", id_list[num], " utente numero: ", num, " ...ATTENDERE... Righe da processare: ", fix_count
                                timestamp1 = str(fix[1])
                                timestamp2 = str(appoggio)
                                t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                                t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                                difference = t1-t2
                                if (difference.seconds) < 30:
                                    aoi_list_intermedia.append(sel_aoi)
                                else:
                                    aoi_list.append(aoi_list_intermedia)
                                    aoi_list_intermedia = []
                                    aoi_list_intermedia.append(sel_aoi)
                            else:
                                sel_near_aoi = selectAoiOrNearAoi(conn, cursor, 'fix_out', fix[0], fix[1], fix[2], fix[3])
                                print "out ", id_list[num], " utente numero: ", num, " ...ATTENDERE... Righe da processare: ", fix_count
                                timestamp1 = str(fix[1])
                                timestamp2 = str(appoggio)
                                t1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
                                t2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
                                difference = t1-t2
                                if (difference.seconds) < 30:
                                    aoi_list_intermedia.append(sel_near_aoi)
                                else:
                                    aoi_list.append(aoi_list_intermedia)
                                    aoi_list_intermedia = []
                                    aoi_list_intermedia.append(sel_near_aoi)
                            fix_count = fix_count - 1
                            appoggio = fix[1]
                        aoi_list.append(aoi_list_intermedia)
                        num_saccade = -1
                        for saccade in aoi_list:
                            num_saccade = num_saccade + 1
                            print "SACCADE NUMERO ", num_saccade
                            num_aoi = -1
                            for aoi_sacc in saccade:
                                num_aoi = num_aoi + 1
                                print num_aoi, " --- AOI NUMERO ", aoi_list[num_saccade][num_aoi]
                                insertToTable(conn, cursor, 'saccades', id_list[num], num_saccade, aoi_list[num_saccade][num_aoi], 'NULL', 'NULL')
                    else:
                        saccade_for_user = selectFromTableWhere(conn, cursor, 'saccades', 'id_user order by id_row', id_list[num])
                        for saccade in saccade_for_user:
                            print "Sguardo numero: ", saccade[2], " - Verso l'aoi: ", saccade[3]
                iter = False
            else:
                print "Numero non valido."

def calcMatrEmis(conn, cursor):
    num_fix_in = countRowTable(cursor, 'fix_in')
    num_fix_out = countRowTable(cursor, 'fix_out')
    if num_fix_in != 0 and num_fix_out != 0:
        count_near_aoi_null = countRowTableWhere(conn, cursor, 'fix_out', 'near_aoi', 'IS NULL', 'NULL', 'NULL')
        if count_near_aoi_null == 0:
            count_emis = countRowTable(cursor, 'emissione')
            if count_emis == 0:
                count_aoi = countRowTable(cursor, 'aoi')
                id_distinct = selectFromTableWhere(conn, cursor, 'db', 'id_user DISTINCT', 'NULL')
                m = []
                u = 0
                for i in range(1, count_aoi + 1):
                    mat = []
                    coeff = 0
                    for id in id_distinct:
                        count_fix_in = countRowTableWhere(conn, cursor, 'fix_in', 'id_user', id[0], 'aoi', i)
                        count_fix_out = countRowTableWhere(conn, cursor, 'fix_out', 'id_user', id[0], 'near_aoi', i)
                        totale = count_fix_in + count_fix_out
                        mat.append(totale)
                        print "L'utente", id[0], "guarda direttamente o in prossimita dell'aoi", i, "per", totale, "volte"
                        coeff = coeff + totale
                    n = 0
                    for id in id_distinct:
                        mat[n] = Decimal(mat[n]) / Decimal(coeff)
                        print "L\'utente ", id[0], " ha probabilita' ", mat[n], " di guardare l\aoi ", i
                        insertToTable(conn, cursor, 'emissione', id[0], i, mat[n], 'NULL', 'NULL')
                        n = n + 1
                    m.append(mat)
            else:
                emissione = selectFromTable(cursor, 'emissione')
                for prob in emissione:
                    print "L\'utente ", prob[0], " ha probabilita' ", prob[2], " di guardare l\'aoi ", prob[1]
        else:
            print "\nImpossibile calcolare la matrice di emissione se prima non sono state calcolate le AOI piu' vicine agli sguardi esterni.\n Selezionare l'opzione 4"
    else:
        print "\nImpossibile calcolare la matrice di emissione se prima non sono stati divisi gli utenti che guardano all'esterno o all'interno di una AOI.\n Selezionare l'opzione 1"

def calcMatrTrans(conn, cursor):
    cursor.execute("SELECT * FROM saccades")
    saccades = cursor.fetchall()
    num_saccades = cursor.rowcount
    if num_saccades != 0:
        cursor.execute("SELECT * FROM transizione")
        trans = cursor.fetchall()
        num_row_transizione = cursor.rowcount
        if num_row_transizione == 0:
            cursor.execute("SELECT * FROM aoi")
            num_aoi = cursor.rowcount
            r1 = []
            r2 = []
            r3 = []
            r4 = []
            r5 = []
            r6 = []
            r7 = []
            r8 = []
            for i in range (0,num_aoi):
                r1.append(0)
            for i in range (0,num_aoi):
                r2.append(0)
            for i in range (0,num_aoi):
                r3.append(0)
            for i in range (0,num_aoi):
                r4.append(0)
            for i in range (0,num_aoi):
                r5.append(0)
            for i in range (0,num_aoi):
                r6.append(0)
            for i in range (0,num_aoi):
                r7.append(0)
            for i in range (0,num_aoi):
                r8.append(0)
            m = [ ]
            m.append(r1)
            m.append(r2)
            m.append(r3)
            m.append(r4)
            m.append(r5)
            m.append(r6)
            m.append(r7)
            m.append(r8)
            appoggio1 = 0
            appoggio2 = 0
            appoggio3 = 0
            for saccade in saccades:
                if saccade[1] == appoggio1 and saccade[2] == appoggio2:
                    aoi_1 = appoggio3
                    aoi_2 = saccade[3]
                    print aoi_1, aoi_2
                    elem = m[aoi_1-1]
                    elem[aoi_2-1] = elem[aoi_2 - 1] + 1
                appoggio1 = saccade[1]
                appoggio2 = saccade[2]
                appoggio3 = saccade[3]
            print m
            for i in range (0,8):
                somma = 0
                for j in range (0,8):
                    somma = somma + m[i][j]
                print "La somma della riga", i + 1, "e'", somma
                for j in range (0,8):
                    m[i][j] = Decimal(m[i][j])/Decimal(somma)
                    cursor.execute("INSERT INTO transizione (aoi_partenza, aoi_arrivo, probabilita) VALUES (%s, %s, %s)", (i + 1, j + 1, m[i][j]))
                    conn.commit()
        else:
            print "Matrice di transizione gia' calcolata."
            for row_trans in trans:
                print row_trans                   
    else:
        print "\nImpossibile calcolare la matrice di transizione se prima non e' stato calcolato il movimento degli sguardi di ogni utente. \n Selezionare l'opzione 6."

def hmm():

    ##############################################################
    # Prepare parameters for a 4-components HMM
    # Initial population probability
    startprob = np.array([0.6, 0.3, 0.1, 0.0])
    # The transition matrix, note that there are no transitions possible
    # between component 1 and 3
    transmat = np.array([[0.7, 0.2, 0.0, 0.1],
                         [0.3, 0.5, 0.2, 0.0],
                         [0.0, 0.3, 0.5, 0.2],
                         [0.2, 0.0, 0.2, 0.6]])
    # The means of each component
    means = np.array([[0.0,  0.0],
                      [0.0, 11.0],
                      [9.0, 10.0],
                      [11.0, -1.0]])
    # The covariance of each component
    covars = .5 * np.tile(np.identity(2), (4, 1, 1))

    # Build an HMM instance and set parameters
    model = hmm.GaussianHMM(n_components=4, covariance_type="full")

    # Instead of fitting it from the data, we directly set the estimated
    # parameters, the means and covariance of the components
    model.startprob_ = startprob
    model.transmat_ = transmat
    model.means_ = means
    model.covars_ = covars
    ###############################################################

    # Generate samples
    X, Z = model.sample(500)

    # Plot the sampled data
    plt.plot(X[:, 0], X[:, 1], ".-", label="observations", ms=6,
             mfc="orange", alpha=0.7)

    # Indicate the component numbers
    for i, m in enumerate(means):
        plt.text(m[0], m[1], 'Component %i' % (i + 1),
                 size=17, horizontalalignment='center',
                 bbox=dict(alpha=.7, facecolor='w'))
    plt.legend(loc='best')
    plt.show()

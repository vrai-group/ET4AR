'''
Created on 28 ott 2016

@author: simon
'''
import sys
import MySQLdb

from Model.Database import *
from Control.Functionality import *

def main():
    try:
        conn = MySQLdb.connect(host = "localhost", user = "root", passwd="", db="eye_tracking")

        cursor = conn.cursor()
        createTables(cursor)
        itera = True #permette di far ricomparire a video il menu, ad ogni termine di operazione
        while itera:
            menu = input('\nDigita:\n 1 - Per dividere le fixations avvenute all\'interno di una AOI e all\'esterno;\n 2 - Per visualizzare le fixations avvenute all\'interno di una specifica AOI;\n 3 - Per visualizzare le fixations avvenute all\'esterno di una specifica AOI;\n 4 - Per calcolare l\'AOI osservata da ogni fixation;\n 5 - Per calcolare l\'AOI piu\' vicina ad ogni fixations esterna;\n 6 - Per visualizzare le saccades di uno specifico utente;\n 7 - Per calcolare la matrice di emissione;\n 8 - Per calcolare la matrice di transizione;\n 9 - Hidden Markov Model;\n 0 - Per uscire dal programma.\n')
            if menu == 1:
                divFix(conn, cursor)
            elif menu == 2:
                fixInAoi(conn, cursor)
            elif menu == 3:
                fixOutAoi(conn, cursor)
            elif menu == 4:
                aoiFixIn(conn, cursor)
            elif menu == 5:
                nearAoiFixOut(conn, cursor)
            elif menu == 6:
                viewSaccadesOfUser(conn, cursor)
            elif menu == 7:
                calcMatrEmis(conn, cursor)
            elif menu == 8:
                calcMatrTrans(conn, cursor)
            elif menu == 9:
                hiddenMarkovModel(conn, cursor)
            elif menu == 0:
                print 'Arrivederci!'
                itera = False
            else:
                print 'Hai digitato un numero non consentito'
    except MySQLdb.Error, e: #Printa l'errore in caso di presenza dello stesso
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    finally: #infine si chiude la connessione
        if conn:
            conn.close()

if __name__ == '__main__':
    main()
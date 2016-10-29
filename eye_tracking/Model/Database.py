'''
Created on 28 ott 2016

@author: simon
'''

def createTables(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS fix_in (id_user VARCHAR(15), timestamp TIMESTAMP NULL DEFAULT NULL, x DECIMAL(4,2), y DECIMAL(4,2), aoi INT(2));")
    cursor.execute("CREATE TABLE IF NOT EXISTS fix_out (id_user VARCHAR(15), timestamp TIMESTAMP NULL DEFAULT NULL, x DECIMAL(4,2), y DECIMAL(4,2), near_aoi INT(2));")
    cursor.execute("CREATE TABLE IF NOT EXISTS saccades (id_row INT NOT NULL AUTO_INCREMENT PRIMARY KEY, id_user VARCHAR(15), saccade INT(2), aoi INT(2));")
    cursor.execute("CREATE TABLE IF NOT EXISTS emissione (id_user VARCHAR(15), aoi INT(2), probabilita DECIMAL(6,5));")
    cursor.execute("CREATE TABLE IF NOT EXISTS transizione (aoi_partenza INT(2), aoi_arrivo INT(2), probabilita DECIMAL(11,10));")

def selectFromTable(cursor, table):
    if table == 'fix_in':
        cursor.execute("SELECT * FROM fix_in")
        table_fetchall = cursor.fetchall()
    elif table == 'fix_out':
        cursor.execute("SELECT * FROM fix_out")
        table_fetchall = cursor.fetchall()
    elif table == 'aoi':
        cursor.execute("SELECT * FROM aoi")
        table_fetchall = cursor.fetchall()
    elif table == 'db':
        cursor.execute("SELECT * FROM db")
        table_fetchall = cursor.fetchall()
    return table_fetchall

def countRowTable(cursor, table):
    if table == 'fix_in':
        cursor.execute("SELECT * FROM fix_in")
        table_rowcount = cursor.rowcount
    elif table == 'fix_out':
        cursor.execute("SELECT * FROM fix_out")
        table_rowcount = cursor.rowcount
    elif table == 'aoi':
        cursor.execute("SELECT * FROM aoi")
        table_rowcount = cursor.rowcount
    elif table == 'db':
        cursor.execute("SELECT * FROM db")
        table_rowcount = cursor.rowcount
    return table_rowcount

def selectFromTableWhere(conn, cursor, table, col1, val1):
    if table == 'fix_in':
        if col1 == 'aoi':
            cursor.execute("SELECT * FROM fix_in WHERE aoi = %s", val1)
            conn.commit()
        table_fetchall = cursor.fetchall()
    elif table == 'fix_out':
        if col1 == 'near_aoi':
            if val1 == 'IS NULL':
                cursor.execute("SELECT * FROM fix_out WHERE near_aoi IS NULL")
                conn.commit()
            else:
                cursor.execute("SELECT * FROM fix_out WHERE near_aoi = %s", val1)
                conn.commit()
            table_fetchall = cursor.fetchall()
    elif table == 'saccades':
        if col1 == 'id_user':
            cursor.execute("SELECT * FROM saccades WHERE id_user = %s", val1)
            conn.commit()
        elif col1 == 'id_user order by id_row':
            cursor.execute("SELECT * FROM saccades WHERE id_user = %s ORDER BY id_row ASC", val1)
            conn.commit()
        table_fetchall = cursor.fetchall()
    elif table == 'db':
        if col1 == 'id_user order by timestamp':
            cursor.execute("SELECT * FROM db WHERE id_user = %s ORDER BY timestamp ASC", val1)
            conn.commit()
        table_fetchall = cursor.fetchall()
    return table_fetchall

def countRowTableWhere(conn, cursor, table, col1, val1):
    if table == 'fix_in':
        if col1 == 'aoi':
            cursor.execute("SELECT * FROM fix_in WHERE aoi = %s", val1)
            conn.commit()
        table_rowcount = cursor.rowcount
    elif table == 'fix_out':
        if col1 == 'near_aoi':
            if val1 == 'IS NULL':
                cursor.execute("SELECT * FROM fix_out WHERE near_aoi IS NULL")
                conn.commit()
            else:
                cursor.execute("SELECT * FROM fix_out WHERE near_aoi = %s", val1)
                conn.commit()
            table_rowcount = cursor.rowcount
    elif table == 'saccades':
        if col1 == 'id_user':
            cursor.execute("SELECT * FROM saccades WHERE id_user = %s", val1)
            conn.commit()
        table_rowcount = cursor.rowcount
    elif table == 'db':
        if col1 == 'id_user order by timestamp':
            cursor.execute("SELECT * FROM db WHERE id_user = %s ORDER BY timestamp ASC", val1)
            conn.commit()
        table_rowcount = cursor.rowcount
    return table_rowcount

def insertToTable(conn, cursor, table, val1, val2, val3, val4, val5):
    if table == 'fix_in':
        cursor.execute("INSERT INTO fix_in (id_user, timestamp, x, y, aoi) VALUES (%s, %s, %s, %s, %s)", (val1, val2, val3, val4, val5))
    elif table == 'fix_out':
        cursor.execute("INSERT INTO fix_out (id_user, timestamp, x, y) VALUES (%s, %s, %s, %s)", (val1, val2, val3, val4))
    elif table == 'saccades':
        cursor.execute("INSERT INTO saccades (id_user, saccade, aoi) VALUES (%s, %s, %s)", (val1, val2, val3))
    elif table == 'emissione':
        cursor.execute("INSERT INTO emissione (id_user, aoi, probabilita) VALUES (%s, %s, %s)", (val1, val2, val3))
    elif table == 'transizione':
        cursor.execute("INSERT INTO transizione (aoi_partenza, aoi_arrivo, probabilita) VALUES (%s, %s, %s)", (val1, val2, val3))
    conn.commit()

def selectAoiOrNearAoi(conn, cursor, table, val1, val2, val3, val4):
    if table == 'fix_in':
        cursor.execute("SELECT aoi FROM fix_in WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (val1, val2, val3, val4))
    elif table == 'fix_out':
        cursor.execute("SELECT near_aoi FROM fix_out WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (val1, val2, val3, val4))
    conn.commit()
    table_fetchall = cursor.fetchall()
    return table_fetchall

def countAoiOrNearAoi(conn, cursor, table, val1, val2, val3, val4):
    if table == 'fix_in':
        cursor.execute("SELECT aoi FROM fix_in WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (val1, val2, val3, val4))
    elif table == 'fix_out':
        cursor.execute("SELECT near_aoi FROM fix_out WHERE id_user = %s AND timestamp = %s AND x = %s AND y = %s", (val1, val2, val3, val4))
    conn.commit()
    table_rowcount = cursor.rowcount
    return table_rowcount
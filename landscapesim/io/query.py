import sqlite3


def ssim_query(smt, library):
    """ Connect to a SyncroSim sqlite database, and execute a query and return data. """
    with sqlite3.connect(library.file) as con:
        cur = con.cursor()
        cur.execute(smt)
        data = cur.fetchall()
    return data

import sqlite3


def ssim_query(smt, library):

    with sqlite3.connect(library.file) as con:

        cur = con.cursor()
        cur.execute(smt)
        data = cur.fetchall()

    return data

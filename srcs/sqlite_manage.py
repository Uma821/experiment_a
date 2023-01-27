import sqlite3

dbname = "user_info.db"
conn = sqlite3.connect(dbname) # DB作成 or 接続

def createNewRow(userid):
  pass

if __name__ == "__main__":
    # SQLiteを操作するためのカーソルを作成
    cur = conn.cursor()
    # テーブルの作成
    cur.execute(
        'CREATE TABLE items(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, price INTEGER)'
    )

    conn.close()
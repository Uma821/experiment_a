import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import sqlite3
import lineconfig, urlconfig

conn = sqlite3.connect(lineconfig.USER_INFO_DB_PATH, check_same_thread=False) # DB作成 or 接続 別スレッドからのアクセスを防がない
# SQLiteを操作するためのカーソルを作成
cur = conn.cursor()
# テーブルの作成(存在しなければ作成する)
cur.execute("""
    CREATE TABLE IF NOT EXISTS
    schedule(id TEXT PRIMARY KEY, def_outbound_url TEXT NOT NULL, def_inbound_url TEXT NOT NULL)
    """)
conn.commit()

def DB_create_new_row(userid):
    cur.execute('INSERT INTO schedule VALUES(?, ?, ?)', (userid, urlconfig.OUTBOUND_URL, urlconfig.INBOUND_URL))
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS
        schedule{userid}(url TEXT, out_in INTEGER NOT NULL, weekday INTEGER NOT NULL, start_hour INTEGER NOT NULL, start_min INTEGER NOT NULL, end_hour INTEGER NOT NULL, end_min INTEGER NOT NULL)
        """)
    conn.commit() # 一段落ついたら保存

def DB_update_schedule_data(userid, def_outbound_url, def_inbound_url, schedule_time_list):
    cur.execute('UPDATE schedule set def_outbound_url=?,def_inbound_url=? where id=?', (eval(def_outbound_url),eval(def_inbound_url),userid))

    cur.execute(f'DELETE FROM schedule{userid}') # テーブルの中身全消し
    # cur.execute(f'DELETE FROM sqlite_sequence WHERE name = schedule{userid}')
    for (url,out_in,weekday,start_hour,start_min,end_hour,end_min) in schedule_time_list:
        cur.execute(f'INSERT INTO schedule{userid} VALUES(?,?,?,?,?,?,?)', (eval(url),eval(out_in),eval(weekday),eval(start_hour),eval(start_min),eval(end_hour),eval(end_min)))
    conn.commit() # 一段落ついたら保存

def DB_delete_schedule_data(userid):
    cur.execute('DELETE from schedule where id = ?', (userid,))
    cur.execute(f'DROP TABLE IF EXISTS schedule{userid}') # 存在するならテーブル削除
    conn.commit() # 一段落ついたら保存

def find_cursor_people(default_cursor_dict):
    from datetime import datetime, timedelta, timezone
    # JSTタイムゾーンを作成
    jst = timezone(timedelta(hours=9), 'JST')
    now_time = datetime.now(jst)

    cur.execute("SELECT * FROM schedule")
    for (userid,def_outbound_url,def_inbound_url) in cur.fetchall():
        cur.execute(f"SELECT * FROM schedule{userid}")
        for (url,out_in,weekday,start_hour,start_min,end_hour,end_min) in cur.fetchall():
            if now_time.weekday() == weekday and now_time.replace(hour=start_hour, minute=start_min) <= now_time <= now_time.replace(hour=end_hour, minute=end_min): # 今該当するか
                scraping_url = (def_outbound_url if out_in == 0 else def_inbound_url) if url is None else url
                default_cursor_dict[scraping_url] = default_cursor_dict.get(scraping_url, {}) | {userid}

def DB_close():
    conn.close()

if __name__ == "__main__":

    conn.close()
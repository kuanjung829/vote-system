import sqlite3
import uuid

# 定義資料庫檔案名稱
DB_FILE = "system.db"

def init_db():
    # 建立連線（如果 system.db 檔案不存在，SQLite 會自動幫我們建立）
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 啟用 SQLite 的外鍵約束 (Foreign Key) 支援
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("開始建立資料表...")

    # 1. 建立管理員表 (Admins)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Admins (
            id TEXT PRIMARY KEY,
            account TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # 2. 建立投票主題表 (Polls)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Polls (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. 建立投票選項表 (PollOptions) - 關聯到 Polls
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PollOptions (
            id TEXT PRIMARY KEY,
            poll_id TEXT NOT NULL,
            option_text TEXT NOT NULL,
            vote_count INTEGER DEFAULT 0,
            FOREIGN KEY (poll_id) REFERENCES Polls (id) ON DELETE CASCADE
        )
    ''')

    # 4. 建立留言主題表 (Topics)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Topics (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. 建立留言內容表 (Comments) - 關聯到 Topics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments (
            id TEXT PRIMARY KEY,
            topic_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (topic_id) REFERENCES Topics (id) ON DELETE CASCADE
        )
    ''')

    # 6. 建立投票防弊歷史表 (VotesHistory) - 關聯到 Polls
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VotesHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_uuid TEXT NOT NULL,
            poll_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (poll_id) REFERENCES Polls (id) ON DELETE CASCADE
        )
    ''')

    # 提交變更並關閉連線
    conn.commit()
    conn.close()
    print("✅ 所有資料表建立完成！系統已準備就緒。")

if __name__ == "__main__":
    init_db()
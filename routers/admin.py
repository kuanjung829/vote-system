from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import List
import sqlite3
import hashlib
import uuid
from auth import create_jwt_token, verify_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])
DB_FILE = "system.db"

# 讓前端能傳送新帳號與密碼過來
class AdminCreate(BaseModel):
    account: str
    password: str
# --- Pydantic 接收資料模型 ---
class LoginData(BaseModel):
    account: str
    password: str

# 讓前端能一次傳送「標題」跟「所有選項陣列」過來
class PollCreate(BaseModel):
    title: str
    options: List[str] 

# --- 工具函數 ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# 1. 管理員登入 API
# ==========================================
@router.post("/login")
def admin_login(data: LoginData, response: Response):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash FROM Admins WHERE account = ?", (data.account,))
    admin = cursor.fetchone()
    input_hash = hash_password(data.password)

    # 創始管理員機制
    if not admin:
        cursor.execute("SELECT COUNT(*) FROM Admins")
        if cursor.fetchone()[0] == 0:
            admin_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO Admins (id, account, password_hash) VALUES (?, ?, ?)", 
                           (admin_id, data.account, input_hash))
            conn.commit()
            admin = (admin_id, input_hash)
        else:
            conn.close()
            raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    conn.close()

    if admin[1] != input_hash:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    token = create_jwt_token(data={"sub": admin[0], "role": "admin"})
    response.set_cookie(key="admin_token", value=token, httponly=True, samesite="lax")
    return {"message": "管理員登入成功"}

# ==========================================
# 2. 新增投票專案 API (受 JWT 保護)
# ==========================================
@router.post("/polls", dependencies=[Depends(verify_admin)])
def create_poll(poll_data: PollCreate):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    poll_id = str(uuid.uuid4())
    
    # 寫入主表 (Polls)
    cursor.execute("INSERT INTO Polls (id, title, is_active) VALUES (?, ?, 1)", 
                   (poll_id, poll_data.title))
    
    # 寫入關聯子表 (PollOptions)
    for opt_text in poll_data.options:
        opt_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO PollOptions (id, poll_id, option_text, vote_count) VALUES (?, ?, ?, 0)",
                       (opt_id, poll_id, opt_text))
        
    conn.commit()
    conn.close()
    
    return {"message": "投票項目建立成功", "poll_id": poll_id}

# ==========================================
# 3. 取得所有投票與數據 API (受 JWT 保護)
# ==========================================
@router.get("/polls", dependencies=[Depends(verify_admin)])
def get_all_polls():
    conn = sqlite3.connect(DB_FILE)
    # 讓 SQLite 撈出來的資料變成字典格式 (dict)，方便轉成 JSON
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    # 撈取所有投票 (包含已關閉)
    cursor.execute("SELECT * FROM Polls ORDER BY created_at DESC")
    polls = [dict(row) for row in cursor.fetchall()]
    
    # 幫每個投票撈取底下對應的選項與票數
    for poll in polls:
        cursor.execute("SELECT id, option_text, vote_count FROM PollOptions WHERE poll_id = ?", (poll["id"],))
        poll["options"] = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return polls

# ==========================================
# 4. 關閉投票 API (受 JWT 保護)
# ==========================================
@router.put("/polls/{poll_id}/close", dependencies=[Depends(verify_admin)])
def close_poll(poll_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE Polls SET is_active = 0 WHERE id = ?", (poll_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="找不到該投票項目")
        
    conn.commit()
    conn.close()
    return {"message": "投票已成功關閉"}
# 1. 請在檔案最上方的 Pydantic 模型區塊，補上這個模型：
class TopicCreate(BaseModel):
    title: str

# 2. 將以下兩個 API 貼到 admin.py 的最下方：

# ==========================================
# 5. 新增留言主題 API (受 JWT 保護)
# ==========================================
@router.post("/topics", dependencies=[Depends(verify_admin)])
def create_topic(topic_data: TopicCreate):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    topic_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO Topics (id, title, is_active) VALUES (?, ?, 1)", 
                   (topic_id, topic_data.title))
    
    conn.commit()
    conn.close()
    return {"message": "留言主題建立成功", "topic_id": topic_id}

# ==========================================
# 6. 刪除不當留言 API (受 JWT 保護)
# ==========================================
@router.delete("/comments/{comment_id}", dependencies=[Depends(verify_admin)])
def delete_comment(comment_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Comments WHERE id = ?", (comment_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="找不到該則留言")
        
    conn.commit()
    conn.close()
    return {"message": "留言已成功刪除"}
# ==========================================
# 7. 管理員登出 API
# ==========================================
@router.post("/logout")
def admin_logout(response: Response):
    # 將 admin_token 這個 Cookie 的過期時間設定為過去，藉此讓瀏覽器刪除它
    response.delete_cookie(key="admin_token", httponly=True, samesite="lax")
    return {"message": "已成功登出"}
# ==========================================
# 8. 新增管理員帳號 API (受 JWT 保護)
# ==========================================
@router.post("/accounts", dependencies=[Depends(verify_admin)])
def create_admin_account(data: AdminCreate):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 檢查帳號是否已經被註冊過
    cursor.execute("SELECT id FROM Admins WHERE account = ?", (data.account,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="這個帳號已經被註冊過了喔！")
    
    # 產生新 UUID 並加密密碼
    admin_id = str(uuid.uuid4())
    input_hash = hash_password(data.password)
    
    # 寫入資料庫
    cursor.execute("INSERT INTO Admins (id, account, password_hash) VALUES (?, ?, ?)", 
                   (admin_id, data.account, input_hash))
    
    conn.commit()
    conn.close()
    return {"message": f"成功新增管理員帳號：{data.account}"}
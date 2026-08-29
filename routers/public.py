from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
import sqlite3
import uuid
import jwt
from datetime import timedelta
from auth import create_jwt_token, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/public", tags=["Public"])
DB_FILE = "system.db"

class VoteData(BaseModel):
    option_id: str

# ==========================================
# 1. 取得所有「開放中」的投票項目
# ==========================================
@router.get("/polls")
def get_active_polls():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 只要 is_active = 1 (開放中) 的項目
    cursor.execute("SELECT id, title, created_at FROM Polls WHERE is_active = 1 ORDER BY created_at DESC")
    polls = [dict(row) for row in cursor.fetchall()]
    
    for poll in polls:
        cursor.execute("SELECT id, option_text, vote_count FROM PollOptions WHERE poll_id = ?", (poll["id"],))
        poll["options"] = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return polls

# ==========================================
# 2. 匿名投票 API (核心防作弊機制)
# ==========================================
@router.post("/polls/{poll_id}/vote")
def vote(poll_id: str, vote_data: VoteData, request: Request, response: Response):
    # 1. 檢查並解析訪客憑證 (guest_token)
    guest_token = request.cookies.get("guest_token")
    guest_uuid = None
    
    if guest_token:
        try:
            payload = jwt.decode(guest_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("role") == "guest":
                guest_uuid = payload.get("sub")
        except jwt.InvalidTokenError:
            pass # 憑證無效或過期，稍後直接發配一個新的
            
    # 如果完全沒投過票 (沒有 UUID)，就給他一個全新的身分證字號
    if not guest_uuid:
        guest_uuid = str(uuid.uuid4())

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 2. 檢查投票項目狀態
    cursor.execute("SELECT is_active FROM Polls WHERE id = ?", (poll_id,))
    poll = cursor.fetchone()
    if not poll:
        conn.close()
        raise HTTPException(status_code=404, detail="找不到此投票項目")
    if poll[0] == 0:
        conn.close()
        raise HTTPException(status_code=400, detail="此投票已關閉")

    # 3. 🛡️ 防作弊檢查：查驗此 UUID 是否投過這個項目
    cursor.execute("SELECT id FROM VotesHistory WHERE guest_uuid = ? AND poll_id = ?", (guest_uuid, poll_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail="哎呀，你已經投過這個項目囉！")

    # 4. 驗證通過，執行投票：票數 +1
    cursor.execute("UPDATE PollOptions SET vote_count = vote_count + 1 WHERE id = ? AND poll_id = ?", 
                   (vote_data.option_id, poll_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=400, detail="無效的選項")

    # 5. 將作案紀錄寫入歷史表
    cursor.execute("INSERT INTO VotesHistory (guest_uuid, poll_id) VALUES (?, ?)", (guest_uuid, poll_id))
    
    conn.commit()
    conn.close()

    # 6. 發放長效型 JWT (期限設為 365 天) 存入 Cookie
    new_token = create_jwt_token(data={"sub": guest_uuid, "role": "guest"}, expires_delta=timedelta(days=365))
    # max_age=31536000 代表這塊餅乾會在瀏覽器存活一年
    response.set_cookie(key="guest_token", value=new_token, httponly=True, samesite="lax", max_age=31536000)

    return {"message": "投票成功！"}
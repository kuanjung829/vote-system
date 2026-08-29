from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
import sqlite3
import hashlib
import uuid
from auth import create_jwt_token, verify_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])
DB_FILE = "system.db"

class LoginData(BaseModel):
    account: str
    password: str

# 密碼加密函數 (SHA-256)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/login")
def admin_login(data: LoginData, response: Response):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 尋找資料庫有沒有這個帳號
    cursor.execute("SELECT id, password_hash FROM Admins WHERE account = ?", (data.account,))
    admin = cursor.fetchone()
    
    input_hash = hash_password(data.password)

    # 【開發小秘訣】如果資料庫目前完全沒有管理員，第一次登入自動成為創始管理員！
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

    # 檢查密碼是否正確
    if admin[1] != input_hash:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    # 登入成功！核發帶有 role: admin 的 JWT Token
    token = create_jwt_token(data={"sub": admin[0], "role": "admin"})
    
    # 將 Token 存入 Cookie 
    # (httponly=True 是防範 XSS 攻擊的核心設定，讓前端 JavaScript 無法竊取這把鑰匙)
    response.set_cookie(key="admin_token", value=token, httponly=True, samesite="lax")
    return {"message": "管理員登入成功"}

# 🔒 測試用的受保護 API，必須有 `verify_admin` 通行證才能進入
@router.get("/dashboard", dependencies=[Depends(verify_admin)])
def get_dashboard():
    return {"message": "歡迎進入最高機密後台！你已經成功通過 JWT 驗證。"}
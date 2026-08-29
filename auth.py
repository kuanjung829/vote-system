import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Request

SECRET_KEY = "my_super_secret_apcs_key" # 這是加密的鑰匙，實務上不會寫死在程式碼裡
ALGORITHM = "HS256"

# 1. 製作 JWT 憑證 (發放通行證)
def create_jwt_token(data: dict, expires_delta: timedelta = timedelta(hours=2)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 2. 驗證 JWT 憑證 (門禁檢查)
def verify_admin(request: Request):
    # 從瀏覽器傳來的 Cookie 中尋找 admin_token
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=401, detail="請先登入管理員帳號")
    
    try:
        # 嘗試用我們的鑰匙解密
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="權限不足，你不是管理員！")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登入已過期，請重新登入")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的憑證")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 👉 新增匯入 public
from routers import admin, public

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
# 👉 將公開路由掛載上去
app.include_router(public.router)

# 允許前端的 Port 來存取 API (前後端分離設定)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載管理員路由
app.include_router(admin.router)
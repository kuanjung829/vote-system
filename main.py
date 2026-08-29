from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import admin

app = FastAPI()

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
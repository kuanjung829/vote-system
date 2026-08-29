# 🗳️ 匿名投票與留言整合系統 (Anonymous Voting & Board System)

這是一個基於 Python FastAPI 打造的全端整合系統，提供輕量級的「匿名投票」與「留言板」功能。
系統採用前後端分離架構，並導入 **JWT (JSON Web Token)** 作為核心認證與防作弊機制，確保管理員操作的安全性，同時實現匿名使用者的精準權限控管。

## ✨ 核心功能 (Features)

### 👤 匿名使用者 (User - 前台)
* **免登入參與**：進入網站即可瀏覽所有「開放中」的投票項目與留言板。
* **投票機制**：點擊選項即可完成投票，系統即時更新數據。
* **防重複投票**：基於 JWT 與 Cookie 簽發「匿名訪客憑證 (Guest Token)」，嚴格限制每個裝置/瀏覽器對單一項目**只能投一次票**。
* **即時結果檢視**：投票完成後，介面自動切換為進度條，顯示各選項的票數與比例。
* **匿名留言**：可在指定的留言板主題下自由發表看法。

### 👑 管理員 (Manager - 後台)
* **JWT 安全認證**：透過帳號密碼登入後，獲取具備時效性的 Manager JWT Token (HTTP-only Cookie)，保護所有後台 API 路由。
* **多重管理員機制**：創始管理員登入後，可在控制面板中建立其他管理員帳號。
* **安全登出機制**：完整的 Token 銷毀機制，確保帳號切換與登出的資訊安全。
* **投票專案管理**：
  * 建立新的投票項目，並自訂多個投票選項。
  * 隨時將投票項目切換為「關閉」，停止接受新選票。
  * 檢視所有（含已關閉）投票項目的最終數據。
* **留言板管理**：
  * 建立新的留言板主題。
  * 擁有最高權限，可直接刪除不當留言。

---

## 🛠️ 技術堆疊 (Tech Stack)

* **後端框架**：Python, FastAPI, Uvicorn
* **資料庫**：SQLite (關聯式資料庫設計，適合處理一對多關聯)
* **認證機制**：JWT (JSON Web Token), PyJWT, HTTP-only Cookies, SHA-256 密碼雜湊
* **前端介面**：原生 HTML5, CSS3, Vanilla JavaScript, Fetch API, LocalStorage

---

## 🔐 核心架構解析：JWT 雙重應用策略

本系統將 JWT 的應用分為兩個維度，兼顧「後台安全」與「前台防作弊」：

1. **Manager Token (管理員通行證)**：
   * 管理員登入成功後簽發，包含 `role: "admin"` 聲明。
   * 用於攔截並保護所有 POST/PUT/DELETE 的後台管理 API。
2. **Guest Token (匿名訪客指紋)**：
   * 當匿名使用者第一次進行投票時，系統在背景自動核發一組帶有 UUID 的 JWT，並存入使用者的 HTTP-only Cookie 中。
   * 後端資料庫的 `VotesHistory` 表會記錄該 UUID 投過的 `poll_id`，完美阻擋惡意刷新或重複發送 API 投票的行為。

---

## 🗄️ 資料庫綱要 (Database Schema)

系統採用 SQLite，包含以下 6 張核心資料表：

| 資料表名稱 | 用途說明 | 核心欄位 |
| :--- | :--- | :--- |
| **Admins** | 管理員帳號 | `id`, `account`, `password_hash` |
| **Polls** | 投票主題 | `id`, `title`, `is_active`, `created_at` |
| **PollOptions** | 投票選項 | `id`, `poll_id` (FK), `option_text`, `vote_count` |
| **Topics** | 留言板主題 | `id`, `title`, `is_active`, `created_at` |
| **Comments** | 留言內容 | `id`, `topic_id` (FK), `content`, `created_at` |
| **VotesHistory**| 投票紀錄(防弊)| `id`, `guest_uuid`, `poll_id` (FK) |

---

## 🚀 開發里程碑 (Roadmap)

- [x] **Phase 1: 基礎建設與資料庫**
  - [x] 初始化 FastAPI 專案結構 (Routers 模組化)。
  - [x] 建立 SQLite 資料庫連線與創建 6 張核心資料表 (具備 Cascade 連鎖刪除)。
- [x] **Phase 2: JWT 認證與管理員 API**
  - [x] 實作 JWT 簽發與解析機制 (Dependency Injection)。
  - [x] 實作管理員登入/登出 API，與新增管理員帳號功能。
  - [x] 實作後台 CRUD API (新增投票/選項、新增主題、刪除留言)。
- [x] **Phase 3: 匿名使用者 API**
  - [x] 實作前台讀取 API (取得開放中的投票與留言)。
  - [x] 實作投票 API (包含 Guest Token 簽發與防重複投票邏輯)。
  - [x] 實作新增留言 API。
- [x] **Phase 4: 前端介面串接與 UI 設計**
  - [x] 實作 `index.html` (前台投票與留言介面)。
  - [x] 實作 `admin.html` (後台指揮官管理介面)。
  - [x] 實作前後端分離的跨 Port (CORS) 串接與 Cookie 傳遞。

---

## 📁 專案目錄架構 (Project Structure)

```text
📦 vote-system
 ┣ 📂 frontend                 # 前端靜態網頁 (Live Server 執行: Port 5500)
 ┃ ┣ 📜 index.html             # 匿名投票與留言板介面
 ┃ ┗ 📜 admin.html             # 最高權限後台控制面板
 ┣ 📂 routers                  # API 路由模組
 ┃ ┣ 📜 admin.py               # 後台管理員 API (受 JWT 保護)
 ┃ ┗ 📜 public.py              # 前台匿名使用者 API (包含投票防作弊機制)
 ┣ 📜 main.py                  # FastAPI 主程式入口 (CORS 設定與路由掛載)
 ┣ 📜 database.py              # SQLite 資料庫初始化腳本 (建立資料表與關聯)
 ┣ 📜 auth.py                  # JWT (JSON Web Token) 簽發與驗證核心邏輯
 ┣ 📜 system.db                # SQLite 資料庫實體檔案 (執行 database.py 後自動產生)
 ┗ 📜 README.md                # 專案說明文件
```

---

## 🚀 本機執行指令 (How to Run)

請確認你的電腦已安裝 Python 3.7+，並跟著以下步驟啟動系統：

### 1. 安裝必要套件
打開終端機，執行以下指令安裝 FastAPI 網頁框架、Uvicorn 伺服器與 JWT 處理套件：
```bash
pip install fastapi uvicorn pyjwt
```

### 2. 初始化資料庫
在專案根目錄下執行資料庫建置腳本。執行後會自動產生 `system.db` 實體檔案與所有關聯資料表：
```bash
python database.py
```

### 3. 啟動 FastAPI 後端伺服器
啟動後端 API 伺服器，預設會運行於 `[http://127.0.0.1:8000](http://127.0.0.1:8000)`：
```bash
uvicorn main:app --reload
```
*(💡 啟動後，你可以前往 `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)` 查看由 FastAPI 自動生成的 Swagger UI API 測試介面)*

### 4. 啟動前端網頁 (前後端分離)
1. 建議在 VS Code 中安裝 **Live Server** 擴充套件。
2. 進入 `frontend` 資料夾，對 `index.html` 或 `admin.html` 點擊右鍵，選擇 **Open with Live Server**。
3. 前端網頁會運行於 `[http://127.0.0.1:5500](http://127.0.0.1:5500)`，並自動跨 Port 呼叫後端 API。

**👑 創始管理員帳號說明：**
本系統具備「創始管理員自動註冊」機制。當資料庫無管理員帳號時，於 `admin.html` 首次輸入的帳號與密碼將自動註冊為最高權限之創始管理員。

---

## 📦 API 詳細規格說明

### Admin Login :

* Desc : 管理員登入。驗證成功後，後端會將包含權限的 JWT 寫入瀏覽器的 HTTP-only Cookie 中。
* Prefix : `/api/admin/login` (POST)
* data :

```json
{
  "account": "admin",
  "password": "password123"
}
```

* return data :

```json
{
  "message": "管理員登入成功"
}
```

---

### Create Admin Account :

* Desc : 建立新的管理員帳號 (需攜帶有效之管理員 JWT Cookie)。
* Prefix : `/api/admin/accounts` (POST)
* data :

```json
{
  "account": "newAdmin",
  "password": "newPassword"
}
```

* return data :

```json
{
  "message": "成功新增管理員帳號：newAdmin"
}
```

---

### Create Poll :

* Desc : 建立新投票專案與關聯選項 (需攜帶有效之管理員 JWT Cookie)。前端僅需傳送標題與選項字串陣列，id 由後端生成。
* Prefix : `/api/admin/polls` (POST)
* data :

```json
{
  "title": "今天晚餐吃什麼？",
  "options": [
    "麥當勞",
    "肯德基",
    "漢堡王"
  ]
}
```

* return data :

```json
{
  "message": "投票項目建立成功",
  "poll_id": "c1f6d3a9-4b2a-4f8a-9c3b-1d7e5f2a8b9c"
}
```

---

### Submit Vote :

* Desc : 匿名使用者進行投票。首次投票會自動獲得一組帶有 UUID 的 Guest Token Cookie。若該 UUID 已投過此 `poll_id`，將回傳 403 錯誤防弊。
* Prefix : `/api/public/polls/{poll_id}/vote` (POST)
* data :

```json
{
  "option_id": "e2a4b6c8-1d3f-5a7b-9c1e-3f5a7b9c1e3f"
}
```

* return data :

```json
{
  "message": "投票成功！"
}
```

---

### Create Topic :

* Desc : 管理員建立新的留言板主題 (需攜帶有效之管理員 JWT Cookie)。
* Prefix : `/api/admin/topics` (POST)
* data :

```json
{
  "title": "對這次 APCS 考試難度的看法？"
}
```

* return data :

```json
{
  "message": "留言主題建立成功",
  "topic_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d"
}
```

---

### Add Comment :

* Desc : 匿名使用者於指定的留言板主題下新增留言。
* Prefix : `/api/public/topics/{topic_id}/comments` (POST)
* data :

```json
{
  "content": "我覺得這次題目偏難，尤其是第三題卡了很久！"
}
```

* return data :

```json
{
  "message": "留言發布成功！"
}
```
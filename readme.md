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
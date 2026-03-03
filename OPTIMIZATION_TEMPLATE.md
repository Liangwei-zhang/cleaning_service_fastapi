# FastAPI 項目優化模板

> 從 MVP 到百萬用戶的完整優化指南

---

## 📋 優化檢查清單

### Phase 1: 基礎加固 (MVP 完成後)

- [x] 環境變量管理 (pydantic-settings)
- [x] 日誌系統 (logging + 中間件)
- [x] 異常處理 (Exception Handler)
- [x] 請求日誌 (Request Logging)
- [x] CORS 配置
- [x] .env.example 模板
- [x] .gitignore 配置

### Phase 2: 數據層優化

- [x] PostgreSQL 升級 (從 SQLite)
- [x] Alembic 數據庫遷移
- [x] Redis 緩存
- [x] 分頁機制 (Pagination)
- [x] 連接池配置

### Phase 3: 媒體優化

- [x] 媒體文件分離 (Base64 → 文件)
- [x] 圖片懶加載 (`loading="lazy"`)
- [x] 音頻懶加載 (`preload="none"`)
- [x] S3/MinIO 存儲支持

### Phase 4: 前端優化

- [x] PWA 支持 (Manifest + Service Worker)
- [x] WebSocket 實時通訊
- [x] API 工具函數 (debounce/throttle)
- [x] XSS 防護 (escapeHtml)

### Phase 5: 部署優化

- [x] Docker + docker-compose
- [x] Nginx 反向代理
- [x] Gunicorn 多 Worker
- [x] 健康檢查端點 (/health)
- [x] 資源限制配置

---

## 📁 標準項目結構

```
project/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── api/
│   │   ├── routes.py       # API 路由
│   │   └── websocket.py     # WebSocket
│   ├── models/
│   │   └── *.py            # SQLModel 模型
│   ├── core/
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 數據庫連接
│   │   └── logging.py      # 日誌
│   └── services/
│       ├── cache.py        # Redis 緩存
│       └── storage.py      # S3 存儲
├── uploads/                 # 上傳文件
│   ├── images/
│   └── voice/
├── alembic/                # 數據庫遷移
├── js/                     # 前端 JS
│   ├── api.js             # API 工具
│   └── websocket.js        # WebSocket 客戶端
├── css/
│   └── styles.css
├── *.html                 # 前端頁面
├── manifest.json           # PWA 配置
├── sw.js                  # Service Worker
├── nginx.conf             # Nginx 配置
├── Dockerfile             # Docker 鏡像
├── docker-compose.yml     # 部署配置
├── requirements.txt        # Python 依賴
├── .env.example          # 環境變量模板
└── .gitignore
```

---

## 🔧 標準依賴

```txt
# Core
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlmodel==0.0.20

# Database
psycopg2-binary==2.9.11
asyncpg==0.30.0
alembic==1.14.0

# Cache & Storage
redis==5.0.0
boto3==1.35.0

# Config
pydantic-settings==2.13.1

# Utils
python-multipart==0.0.12
email-validator==2.3.0
```

---

## ⚙️ 標準環境變量

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_ENABLED=false
REDIS_URL=redis://localhost:6379/0

# S3 Storage
S3_ENABLED=false
S3_ENDPOINT=localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=projectname
S3_PUBLIC_URL=http://localhost:9000/bucket

# Server
HOST=0.0.0.0
PORT=80
DEBUG=false
```

---

## 🐳 標準 Docker Compose

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

  app:
    build: .
    command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:80
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/cleaning
      REDIS_ENABLED: "true"
      REDIS_URL: redis://redis:6379/0

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: cleaning
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  pgdata:
```

---

## 📝 標準 API 路由結構

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["api"])

# ========== 資源 CRUD ==========
@router.get("/resources")
def get_resources(page: int = 1, limit: int = 20):
    """分頁獲取列表"""
    pass

@router.get("/resources/{id}")
def get_resource(id: int):
    """獲取單個資源"""
    pass

@router.post("/resources")
def create_resource(data: dict):
    """創建資源"""
    pass

@router.put("/resources/{id}")
def update_resource(id: int, data: dict):
    """更新資源"""
    pass

@router.delete("/resources/{id}")
def delete_resource(id: int):
    """刪除資源"""
    pass

# ========== 業務操作 ==========
@router.post("/resources/{id}/action")
def resource_action(id: int, data: dict):
    """業務操作"""
    pass

# ========== 統計 ==========
@router.get("/stats")
def get_stats():
    """獲取統計數據"""
    pass

# ========== 上傳 ==========
@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """上傳圖片"""
    pass
```

---

## 🛡️ 安全檢查清單

- [ ] HTTPS 啟用
- [ ] CORS 限制域名
- [ ] Token 過期時間設置
- [ ] Rate Limiting 限流
- [ ] XSS 防護 (escapeHtml)
- [ ] 敏感信息脫敏
- [ ] SQL 注入防護 (ORM)
- [ ] 密碼 Hash (bcrypt)

---

## 📊 性能優化清單

- [ ] 數據庫索引
- [ ] Redis 緩存熱點數據
- [ ] 圖片懶加載
- [ ] Gzip/Brotli 壓縮
- [ ] CDN 靜態資源
- [ ] 分頁查詢
- [ ] WebSocket 實時推送
- [ ] Worker 數量優化

---

## 🚀 部署檢查清單

- [ ] Docker 鏡像構建
- [ ] 健康檢查端點
- [ ] 日誌配置
- [ ] 資源限制設置
- [ ] Nginx 配置
- [ ] 數據庫遷移腳本
- [ ] CI/CD 流水線
- [ ] 備份策略

---

## 📖 使用方法

1. **創建項目時**：複製此模板
2. **優化現有項目**：按階段執行檢查清單
3. **團隊規範**：作為項目標準文檔

---

*最後更新: 2026-03-02*

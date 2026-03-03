# SmartClean 項目優化待辦

> 基於百萬用戶級別的優化建議

---

## Phase 1: 基礎加固 ✅ [已完成]

- [x] 環境變量管理 (pydantic-settings)
- [x] 日誌系統 (logging + 中間件)
- [x] 異常處理 (Exception Handler)
- [x] 請求日誌 (Request Logging)
- [x] CORS 配置
- [x] Alembic 數據庫遷移
- [x] PostgreSQL 升級

---

## Phase 2: 數據層優化 ✅ [已完成]

- [x] Redis 緩存
- [x] 分頁機制 (Pagination)
- [x] S3/MinIO 存儲支持

---

## Phase 3: 前端優化 ✅ [已完成]

- [x] PWA 支持 (Manifest + Service Worker)
- [x] WebSocket 實時通訊
- [x] 圖片懶加載 (`loading="lazy"`)
- [x] 音頻懶加載 (`preload="none"`)
- [x] API 工具函數 (debounce/throttle)
- [x] XSS 防護 (escapeHtml)

---

## Phase 4: 部署優化 ✅ [已完成]

- [x] Docker + docker-compose
- [x] Nginx 反向代理
- [x] Gunicorn 多 Worker
- [x] 健康檢查端點 (/health)
- [x] 資源限制配置

---

## Phase 5: 高級優化 🔲 [待完成]

### 5.1 安全加固

- [ ] Rate Limiting 限流 (防止惡意請求)
- [ ] JWT 身份驗證 (python-jose + passlib)
- [ ] RBAC 角色權限 (Depends 依賴注入)
- [ ] Token 過期時間配置
- [ ] HTTPS/SSL 證書配置
- [ ] 敏感信息脫敏 (手機號遮蔽)
- [ ] HttpOnly Cookie for Refresh Token
- [ ] XSS 防護 (innerHTML → textContent, 22處)

### 5.2 數據庫優化

- [ ] 數據庫索引 (user_id, status, created_at)
- [ ] Query Performance 優化
- [ ] 連接池 Fine-tuning
- [ ] PostGIS 地理空間查詢 (鄰近房源/師傅)
- [ ] Redis 分佈式鎖 (搶單並發控制)
- [ ] 資料庫事務 (ACID)

### 5.3 異步任務

- [ ] Celery / Taskiq 引入
- [ ] 訂單狀態變更推送通知
- [ ] 訂單超時自動取消 (30分鐘)
- [ ] 報表生成任務

### 5.4 前端優化

- [ ] 骨架屏 (Skeleton Screens)
- [ ] WebP 圖片格式轉換
- [ ] srcset 適配不同屏幕
- [ ] Gzip/Brotli 壓縮
- [ ] CDN 靜態資源分發
- [ ] Alpine.js 引入 (輕量框架)

### 5.5 即時功能

- [ ] WebSocket 訂單狀態訂閱
- [ ] 推送通知 (Web Push)
- [ ] 消息已讀回執

### 5.6 運維監控

- [ ] Sentry 錯誤監控
- [ ] Prometheus + Grafana 指標
- [ ] ELK/Loki 日誌收集
- [ ] 數據庫備份策略
- [ ] /health 進階檢查 (DB pool, Redis memory)

### 5.7 CI/CD

- [ ] GitHub Actions 流水線
- [ ] 自動化測試 (Pytest + HTTPX)
- [ ] 自動部署

---

## 優先級排序

| 優先級 | 任務 | 預期收益 |
|--------|------|----------|
| **P0** | Rate Limiting | 系統穩定性 |
| **P0** | JWT 身份驗證 | 安全認證 |
| **P0** | 數據庫索引 | 查詢性能 |
| **P0** | Redis 分佈式鎖 | 搶單併發 |
| **P1** | WebSocket 訂閱 | 實時性 |
| **P1** | CDN | 加載速度 |
| **P1** | PostGIS | 地理查詢 |
| **P2** | 骨架屏 | 用戶體驗 |
| **P2** | 監控 | 運維能力 |
| **P2** | Celery | 異步任務 |
| **P3** | CI/CD | 部署效率 |
| **P3** | Alpine.js | 前端現代化 |

---

## 備註

- Phase 1-4 已完成，生產可用
- Phase 5 根據業務需求選擇性實施
- 百萬用戶時需重點關注 P0-P1 任務

---

## 推薦工具清單

| 分類 | 工具 | 用途 |
|------|------|------|
| 身份驗證 | python-jose, passlib | JWT 簽發與密碼哈希 |
| 異步任務 | Celery / Taskiq | 推播通知與定時任務 |
| 地理位置 | PostGIS | 附近房源與師傅搜索 |
| 測試 | Pytest + HTTPX | 後端 API 覆蓋率測試 |
| 前端 | Alpine.js | 增強原生 JS 交互 |
| 監控 | Sentry | 錯誤追蹤 |
| 監控 | Prometheus + Grafana | 指標可視化 |

---

*最後更新: 2026-03-02*

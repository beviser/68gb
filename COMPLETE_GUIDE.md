# 68GB Game API Crawler - Hướng dẫn Hoàn chỉnh

## 🎯 Tổng quan

Hệ thống này được thiết kế để:
- **Crawl tự động** kết quả game từ 68GB (Tài Xỉu, Bàn Đỏ)
- **Bypass Cloudflare** bằng nhiều phương pháp
- **Cung cấp REST API** để truy xuất dữ liệu
- **Thông báo real-time** qua Telegram, Email, Webhook
- **Deploy dễ dàng** lên Render

## 🚀 Quick Start

### 1. Chạy Local
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy tests và server
python run_local.py

# Hoặc chỉ chạy server
python run_local.py server

# Hoặc chỉ test
python run_local.py test
```

### 2. Deploy lên Render
```bash
# Push lên GitHub
git add .
git commit -m "Deploy 68GB Game API"
git push origin main

# Tạo Web Service trên Render
# - Connect GitHub repo
# - Render tự động detect render.yaml
# - Deploy!
```

## 📁 Cấu trúc Project

```
toolhh/
├── 📂 api/                     # REST API endpoints
│   ├── __init__.py
│   └── routes.py              # API routes chính
├── 📂 crawler/                # Game crawler engine
│   ├── __init__.py
│   └── game_crawler.py        # Crawler với Cloudflare bypass
├── 📂 services/               # Business services
│   ├── __init__.py
│   └── notification_service.py # Telegram/Email/Webhook
├── 📂 backup_*/               # Backup files cũ
├── 📄 main.py                 # FastAPI app entry point
├── 📄 config.py               # Configuration settings
├── 📄 database.py             # SQLAlchemy models
├── 📄 requirements.txt        # Python dependencies
├── 📄 Dockerfile              # Docker configuration
├── 📄 render.yaml             # Render deployment config
├── 📄 .env                    # Environment variables template
├── 📄 run_local.py            # Local development runner
├── 📄 test_api.py             # API testing script
├── 📄 test_crawler.py         # Crawler testing script
└── 📄 README.md               # Documentation
```

## 🔧 Cấu hình

### Environment Variables (.env)
```bash
# Cơ bản
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./game_data.db
GAME_URL=https://68gbvn25.biz/
CRAWL_INTERVAL=30

# Telegram (tùy chọn)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email (tùy chọn)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com

# Webhook (tùy chọn)
WEBHOOK_URL=https://your-webhook.com/endpoint
WEBHOOK_SECRET=your_secret
```

## 🎮 API Endpoints

### Game Information
```bash
GET /api/v1/games                    # Danh sách games
GET /api/v1/games/{game_type}        # Thông tin game
```

### Game Results
```bash
GET /api/v1/games/tai_xiu/latest     # Kết quả mới nhất
GET /api/v1/games/ban_do/latest      # Kết quả mới nhất
GET /api/v1/games/{game}/current     # Crawl trực tiếp (chậm)
GET /api/v1/games/{game}/history     # Lịch sử kết quả
```

### System
```bash
GET /health                          # Health check
GET /api/v1/stats                    # Thống kê hệ thống
POST /api/v1/test-notification       # Test thông báo
```

### Response Format
```json
{
  "game_type": "tai_xiu",
  "results": [
    {
      "id": 1,
      "game_type": "tai_xiu", 
      "session_id": "tai_xiu_1694123456",
      "result_md5": "abc123def456...",
      "result_data": {
        "result": "tai",
        "timestamp": "2023-09-08T10:30:45"
      },
      "timestamp": "2023-09-08T10:30:45"
    }
  ],
  "count": 1
}
```

## 🔍 Testing

### Test API
```bash
python test_api.py
```

### Test Crawler
```bash
python test_crawler.py
```

### Test Production
```bash
# Sửa BASE_URL trong test_api.py
BASE_URL = "https://your-app.onrender.com"
python test_api.py
```

## 🚀 Deployment

### Render (Recommended)
1. **Push lên GitHub**
2. **Tạo Web Service** trên Render
3. **Connect repository**
4. **Auto deploy** từ render.yaml

### Manual Docker
```bash
docker build -t 68gb-api .
docker run -p 8000:8000 68gb-api
```

## 🔔 Notifications

### Telegram Setup
1. Tạo bot với @BotFather
2. Lấy bot token
3. Lấy chat ID từ getUpdates API
4. Set environment variables

### Email Setup
1. Bật 2FA cho Gmail
2. Tạo App Password
3. Set SMTP settings

### Webhook Setup
1. Tạo endpoint nhận webhook
2. Set WEBHOOK_URL và SECRET

## 🛠️ Crawler Features

### Cloudflare Bypass Methods
1. **CloudScraper** - Nhanh nhất
2. **Selenium** - Backup method
3. **Undetected Chrome** - Đáng tin cậy nhất

### Data Processing
- **MD5 hashing** cho kết quả
- **Session tracking** 
- **Duplicate detection**
- **Error handling**

## 📊 Monitoring

### Health Checks
```bash
curl https://your-app.onrender.com/health
```

### Logs
- Render Dashboard → Logs
- Local: `logs/app.log`

### Stats
```bash
curl https://your-app.onrender.com/api/v1/stats
```

## 🔧 Troubleshooting

### Common Issues

**1. Cloudflare Blocking**
- Hệ thống có 3 phương pháp backup
- Kiểm tra logs để xem method nào đang hoạt động

**2. Database Issues**
- SQLite tự động tạo
- Kiểm tra permissions

**3. Notification Failures**
- Test với `/api/v1/test-notification`
- Kiểm tra credentials

**4. Build Failures**
- Kiểm tra requirements.txt
- Xem build logs trong Render

### Debug Commands
```bash
# Local debugging
python run_local.py test

# Check specific game
curl http://localhost:8000/api/v1/games/tai_xiu/current

# Test notifications
curl -X POST http://localhost:8000/api/v1/test-notification
```

## 🔒 Security

- **Environment variables** cho sensitive data
- **No hardcoded secrets** trong code
- **CORS protection**
- **Request logging**

## 📈 Performance

### Render Free Tier Limits
- **750 hours/month** (đủ cho 24/7)
- **Sleep after 15 minutes** inactive
- **Limited bandwidth**

### Optimization
- **Efficient crawling** với interval
- **Database indexing**
- **Async operations**

## 🔄 Updates

### Code Updates
```bash
git add .
git commit -m "Update crawler logic"
git push origin main
# Render auto-redeploys
```

### Configuration Updates
- Update environment variables trong Render Dashboard
- Restart service nếu cần

## 📞 Support

### Self-Help
1. Kiểm tra logs
2. Test health endpoint
3. Verify environment variables
4. Check GitHub Issues

### Monitoring URLs
- **Health**: `https://your-app.onrender.com/health`
- **Stats**: `https://your-app.onrender.com/api/v1/stats`
- **Docs**: `https://your-app.onrender.com/docs`

---

## 🎉 Kết luận

Hệ thống đã sẵn sàng để:
✅ **Crawl** dữ liệu từ 68GB
✅ **Bypass** Cloudflare protection  
✅ **Cung cấp API** cho client
✅ **Thông báo** real-time
✅ **Deploy** lên Render
✅ **Monitor** và maintain

**Next Steps:**
1. Deploy lên Render
2. Cấu hình notifications
3. Test với production data
4. Monitor và optimize

Good luck! 🚀

# Hướng dẫn Deploy 68GB Game API lên Render

## Bước 1: Chuẩn bị Repository

### 1.1 Tạo GitHub Repository
```bash
# Tạo repository mới trên GitHub
# Hoặc sử dụng repository hiện tại
```

### 1.2 Push code lên GitHub
```bash
git init
git add .
git commit -m "Initial commit: 68GB Game API Crawler"
git branch -M main
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```

## Bước 2: Tạo Web Service trên Render

### 2.1 Đăng nhập Render
- Truy cập [render.com](https://render.com)
- Đăng nhập hoặc tạo tài khoản mới
- Kết nối với GitHub account

### 2.2 Tạo Web Service
1. Click **"New +"** → **"Web Service"**
2. Chọn repository GitHub của bạn
3. Cấu hình service:
   - **Name**: `68gb-game-api` (hoặc tên bạn muốn)
   - **Region**: Singapore (gần Việt Nam nhất)
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Plan**: Starter (miễn phí)

### 2.3 Render sẽ tự động detect
- `render.yaml` file
- `Dockerfile`
- Tự động build và deploy

## Bước 3: Cấu hình Environment Variables (Tùy chọn)

Trong Render Dashboard → Service → Environment:

### 3.1 Telegram Notifications (Tùy chọn)
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Cách lấy Telegram Bot Token:**
1. Tìm @BotFather trên Telegram
2. Gửi `/newbot`
3. Đặt tên bot và username
4. Copy token được cung cấp

**Cách lấy Chat ID:**
1. Thêm bot vào group hoặc chat với bot
2. Gửi tin nhắn bất kỳ
3. Truy cập: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Tìm `chat.id` trong response

### 3.2 Email Notifications (Tùy chọn)
```
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com
```

**Lưu ý Gmail:**
- Bật 2-factor authentication
- Tạo App Password thay vì dùng password thường

### 3.3 Webhook Notifications (Tùy chọn)
```
WEBHOOK_URL=https://your-webhook-endpoint.com/webhook
WEBHOOK_SECRET=your_secret_key
```

## Bước 4: Kiểm tra Deployment

### 4.1 Theo dõi Build Process
- Trong Render Dashboard, xem tab **"Logs"**
- Build process sẽ mất 5-10 phút
- Chờ thông báo "Your service is live"

### 4.2 Test API
Sau khi deploy thành công:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# API endpoints
curl https://your-app-name.onrender.com/api/v1/games
```

### 4.3 Test bằng script
```bash
# Sửa BASE_URL trong test_api.py
BASE_URL = "https://your-app-name.onrender.com"

# Chạy test
python test_api.py
```

## Bước 5: Monitoring và Maintenance

### 5.1 Xem Logs
- Render Dashboard → Service → Logs
- Theo dõi crawler activity
- Kiểm tra errors

### 5.2 Health Monitoring
- Render tự động restart nếu service crash
- Health check endpoint: `/health`
- Metrics trong Dashboard

### 5.3 Database Backup
```bash
# Nếu cần backup database
# Tạo endpoint để export data
curl https://your-app-name.onrender.com/api/v1/export
```

## Bước 6: Sử dụng API

### 6.1 API Documentation
- Swagger UI: `https://your-app-name.onrender.com/docs`
- ReDoc: `https://your-app-name.onrender.com/redoc`

### 6.2 Các Endpoint Chính
```bash
# Danh sách games
GET /api/v1/games

# Kết quả mới nhất
GET /api/v1/games/tai_xiu/latest
GET /api/v1/games/ban_do/latest

# Kết quả hiện tại (live crawl)
GET /api/v1/games/tai_xiu/current

# Lịch sử
GET /api/v1/games/tai_xiu/history?limit=50

# Thống kê
GET /api/v1/stats
```

### 6.3 Response Format
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

## Troubleshooting

### Build Failures
1. Kiểm tra Dockerfile syntax
2. Xem build logs trong Render
3. Đảm bảo requirements.txt đúng format

### Runtime Errors
1. Kiểm tra environment variables
2. Xem application logs
3. Test health check endpoint

### Crawler Issues
1. 68GB site có thể thay đổi cấu trúc
2. Cloudflare protection có thể block
3. Cần update crawler logic

### Performance Issues
1. Render Starter plan có giới hạn
2. Cân nhắc upgrade plan nếu cần
3. Optimize crawl interval

## Cập nhật Code

```bash
# Push changes
git add .
git commit -m "Update crawler logic"
git push origin main

# Render sẽ tự động redeploy
```

## Backup và Recovery

### Backup Repository
```bash
# Clone repository
git clone https://github.com/your-username/your-repo-name.git

# Backup database (nếu có)
# Implement export endpoint
```

### Recovery
```bash
# Redeploy từ backup
git push origin main

# Hoặc rollback trong Render Dashboard
```

## Security Notes

1. **Không commit sensitive data** vào repository
2. **Sử dụng Environment Variables** cho secrets
3. **Định kỳ rotate** API keys và tokens
4. **Monitor** unusual activity trong logs

## Support

Nếu gặp vấn đề:
1. Kiểm tra logs trong Render Dashboard
2. Test local trước khi deploy
3. Sử dụng health check endpoints
4. Kiểm tra GitHub Issues

---

**Lưu ý:** Render free tier có một số giới hạn:
- Service sleep sau 15 phút không hoạt động
- 750 giờ/tháng (đủ cho 1 service chạy 24/7)
- Bandwidth và compute limits

Để production use, cân nhắc upgrade lên paid plan.

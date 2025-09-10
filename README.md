# 68GB Game API Crawler

Hệ thống crawl và cung cấp API cho kết quả game từ 68GB, bao gồm Tài Xỉu và Bàn Đỏ với MD5 hash.

## Tính năng

- 🎮 **Crawl tự động**: Thu thập kết quả game từ 68GB với nhiều phương pháp bypass Cloudflare
- 🔄 **Real-time updates**: Cập nhật kết quả game theo thời gian thực
- 📊 **REST API**: Cung cấp API đầy đủ để truy xuất dữ liệu
- 🔔 **Thông báo đa kênh**: Hỗ trợ Telegram, Email, và Webhook
- 💾 **Lưu trữ dữ liệu**: Database SQLite với lịch sử đầy đủ
- 🚀 **Deploy dễ dàng**: Sẵn sàng deploy lên Render

## API Endpoints

### Game Information
- `GET /api/v1/games` - Danh sách games được hỗ trợ
- `GET /api/v1/games/{game_type}` - Thông tin chi tiết game

### Game Results
- `GET /api/v1/games/{game_type}/latest` - Kết quả mới nhất
- `GET /api/v1/games/{game_type}/history` - Lịch sử kết quả
- `GET /api/v1/games/{game_type}/current` - Kết quả hiện tại (crawl trực tiếp)

### System
- `GET /health` - Health check
- `GET /api/v1/stats` - Thống kê hệ thống
- `POST /api/v1/test-notification` - Test thông báo

## Cài đặt Local

### 1. Clone repository
```bash
git clone <repository-url>
cd toolhh
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment
Sao chép `.env` và cập nhật các giá trị:
```bash
cp .env .env.local
# Chỉnh sửa .env.local với cấu hình của bạn
```

### 4. Chạy ứng dụng
```bash
python main.py
```

Ứng dụng sẽ chạy tại `http://localhost:8000`

## Deploy lên Render

### 1. Tạo repository trên GitHub
Push code lên GitHub repository

### 2. Tạo Web Service trên Render
- Kết nối GitHub repository
- Chọn branch `main`
- Render sẽ tự động detect `render.yaml`

### 3. Cấu hình Environment Variables (tùy chọn)
Trong Render dashboard, thêm các biến môi trường:

**Telegram Notifications:**
- `TELEGRAM_BOT_TOKEN`: Token bot Telegram
- `TELEGRAM_CHAT_ID`: Chat ID để gửi thông báo

**Email Notifications:**
- `EMAIL_SMTP_SERVER`: SMTP server (vd: smtp.gmail.com)
- `EMAIL_USERNAME`: Email username
- `EMAIL_PASSWORD`: Email password
- `EMAIL_FROM`: Email gửi
- `EMAIL_TO`: Email nhận

**Webhook Notifications:**
- `WEBHOOK_URL`: URL webhook
- `WEBHOOK_SECRET`: Secret key cho webhook

### 4. Deploy
Render sẽ tự động build và deploy ứng dụng.

## Cấu trúc Project

```
toolhh/
├── api/                    # API routes
│   ├── __init__.py
│   └── routes.py
├── crawler/                # Game crawler
│   ├── __init__.py
│   └── game_crawler.py
├── services/               # Services
│   ├── __init__.py
│   └── notification_service.py
├── config.py              # Cấu hình
├── database.py            # Database models
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── Dockerfile           # Docker configuration
├── render.yaml         # Render deployment config
└── README.md          # Documentation
```

## Game Types Supported

- `tai_xiu`: Tài Xỉu
- `ban_do`: Bàn Đỏ

## Response Format

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
        "timestamp": "2023-09-08T10:30:45",
        "session_id": "tai_xiu_1694123456"
      },
      "timestamp": "2023-09-08T10:30:45"
    }
  ],
  "count": 1
}
```

## Monitoring

- Health check: `GET /health`
- Stats: `GET /api/v1/stats`
- Logs: Xem logs trong Render dashboard

## Troubleshooting

### Cloudflare Issues
Hệ thống sử dụng nhiều phương pháp bypass:
1. CloudScraper
2. Selenium
3. Undetected Chrome

### Browser Issues
- Đảm bảo Chrome được cài đặt
- Kiểm tra ChromeDriver version
- Sử dụng headless mode trong production

### Database Issues
- SQLite database tự động tạo
- Backup định kỳ nếu cần

## Support

Nếu gặp vấn đề, kiểm tra:
1. Logs trong `/logs/app.log`
2. Health check endpoint
3. Environment variables
4. Network connectivity

## License

MIT License

"""
Notification service for sending alerts about new game results
"""
import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime

import httpx
from loguru import logger
from telegram import Bot
from telegram.error import TelegramError

from config import settings

class NotificationService:
    """Service for sending notifications via multiple channels"""
    
    def __init__(self):
        self.telegram_bot = None
        if settings.TELEGRAM_BOT_TOKEN:
            self.telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    async def send_new_result_notification(self, game_type: str, result_data: Dict, result_md5: str):
        """Send notification about new game result"""
        message = self._format_result_message(game_type, result_data, result_md5)
        
        # Send via all configured channels
        tasks = []
        
        if self.telegram_bot and settings.TELEGRAM_CHAT_ID:
            tasks.append(self._send_telegram_notification(message))
        
        if settings.EMAIL_SMTP_SERVER and settings.EMAIL_TO:
            tasks.append(self._send_email_notification(
                subject=f"New {game_type.upper()} Result",
                message=message
            ))
        
        if settings.WEBHOOK_URL:
            tasks.append(self._send_webhook_notification({
                'game_type': game_type,
                'result_data': result_data,
                'result_md5': result_md5,
                'timestamp': datetime.now().isoformat()
            }))
        
        # Execute all notifications concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _format_result_message(self, game_type: str, result_data: Dict, result_md5: str) -> str:
        """Format result data into readable message"""
        game_name = {
            'tai_xiu': 'Tài Xỉu',
            'ban_do': 'Bàn Đỏ'
        }.get(game_type, game_type.upper())
        
        timestamp = result_data.get('timestamp', datetime.now().isoformat())
        result = result_data.get('result', 'N/A')
        session_id = result_data.get('session_id', 'N/A')
        
        message = f"""
🎮 **{game_name} - Kết Quả Mới**

📊 **Kết quả:** {result}
🔑 **MD5:** `{result_md5}`
🆔 **Session:** {session_id}
⏰ **Thời gian:** {timestamp}

---
🔗 **API Endpoint:** `/api/v1/games/{game_type}/latest`
        """.strip()
        
        return message
    
    async def _send_telegram_notification(self, message: str):
        """Send notification via Telegram"""
        try:
            await self.telegram_bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("Telegram notification sent successfully")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram notification: {e}")
    
    async def _send_email_notification(self, subject: str, message: str):
        """Send notification via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = settings.EMAIL_TO
            msg['Subject'] = subject
            
            # Convert markdown to plain text for email
            plain_message = message.replace('**', '').replace('`', '').replace('---', '-' * 50)
            msg.attach(MIMEText(plain_message, 'plain', 'utf-8'))
            
            # Send email
            with smtplib.SMTP(settings.EMAIL_SMTP_SERVER, settings.EMAIL_SMTP_PORT) as server:
                server.starttls()
                if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
                    server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info("Email notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_webhook_notification(self, data: Dict):
        """Send notification via webhook"""
        try:
            headers = {'Content-Type': 'application/json'}
            if settings.WEBHOOK_SECRET:
                headers['X-Webhook-Secret'] = settings.WEBHOOK_SECRET
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.WEBHOOK_URL,
                    json=data,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
            
            logger.info("Webhook notification sent successfully")
        except httpx.HTTPError as e:
            logger.error(f"Failed to send webhook notification: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending webhook notification: {e}")
    
    async def send_system_notification(self, message: str, level: str = "info"):
        """Send system notification (startup, shutdown, errors)"""
        system_message = f"🤖 **System {level.upper()}**\n\n{message}"
        
        tasks = []
        
        if self.telegram_bot and settings.TELEGRAM_CHAT_ID:
            tasks.append(self._send_telegram_notification(system_message))
        
        if settings.WEBHOOK_URL:
            tasks.append(self._send_webhook_notification({
                'type': 'system',
                'level': level,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_test_notification(self):
        """Send test notification to verify configuration"""
        test_message = """
🧪 **Test Notification**

This is a test message to verify notification configuration.

✅ If you receive this message, notifications are working correctly!
        """.strip()
        
        await self.send_system_notification(test_message, "test")
        return True

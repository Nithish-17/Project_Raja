"""
Email service for sending verification alerts
Uses SMTP to send emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

from utils import get_logger, settings

try:
    # Optional Celery import; service still works without worker
    from core.celery_app import celery_app
except Exception:  # pragma: no cover - optional dependency
    celery_app = None


logger = get_logger("email_service")


class EmailService:
    """Service for sending email alerts"""
    
    def __init__(self):
        """Initialize email service"""
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.to_email = settings.smtp_to_email
        logger.info("Email service initialized")
    
    def send_verification_alert(
        self,
        certificate_id: str,
        entities: Dict[str, Any],
        verification_status: str,
        use_celery: bool = True
    ) -> bool:
        """
        Send verification alert email
        
        Args:
            certificate_id: Unique certificate ID
            entities: Extracted entities from certificate
            verification_status: Verification result (VERIFIED, PARTIALLY VERIFIED, NOT VERIFIED)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # When Celery is available, enqueue the task to avoid blocking the request thread
            if use_celery and celery_app:
                celery_app.send_task(
                    "core.celery_app.send_email_task",
                    args=[certificate_id, entities, verification_status],
                    queue="emails",
                )
                logger.info("Email task queued via Celery for %s", certificate_id)
                return True

            # Create email message
            subject = f"Certificate Verification Alert - {certificate_id}"
            body = self._create_email_body(certificate_id, entities, verification_status)
            
            # Send email synchronously
            return self._send_email(subject, body)
            
        except Exception as e:
            logger.error(f"Error sending verification alert: {str(e)}")
            return False
    
    def _create_email_body(
        self,
        certificate_id: str,
        entities: Dict[str, Any],
        verification_status: str
    ) -> str:
        """Create HTML email body"""
        # Determine status color
        status_color = {
            "VERIFIED": "#28a745",
            "PARTIALLY VERIFIED": "#ffc107",
            "NOT VERIFIED": "#dc3545"
        }.get(verification_status, "#6c757d")
        
        # Format entities
        entities_html = ""
        for key, value in entities.items():
            formatted_key = key.replace("_", " ").title()
            entities_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{formatted_key}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{value or 'Not Found'}</td>
            </tr>
            """
        
        # Create HTML body
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f8f9fa; }}
                    .status {{ 
                        font-size: 20px; 
                        font-weight: bold; 
                        color: {status_color}; 
                        padding: 10px; 
                        text-align: center; 
                        margin: 20px 0;
                        border: 2px solid {status_color};
                        border-radius: 5px;
                    }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: white; }}
                    th, td {{ padding: 8px; border: 1px solid #ddd; text-align: left; }}
                    th {{ background-color: #007bff; color: white; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Certificate Verification Report</h1>
                    </div>
                    <div class="content">
                        <h2>Certificate ID: {certificate_id}</h2>
                        
                        <div class="status">
                            Status: {verification_status}
                        </div>
                        
                        <h3>Extracted Entities:</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {entities_html}
                            </tbody>
                        </table>
                        
                        <p style="margin-top: 20px;">
                            <strong>Note:</strong> This is an automated verification alert generated by the 
                            Certificate Verification System.
                        </p>
                    </div>
                    <div class="footer">
                        <p>Certificate Verification System &copy; 2024</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html_body
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send email via SMTP"""
        try:
            # Check if SMTP is configured
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Email not sent.")
                logger.info(f"Email that would be sent:\nSubject: {subject}\n")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = self.to_email
            
            # Attach HTML body
            html_part = MIMEText(body, "html")
            message.attach(html_part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {self.to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False


# Global email service instance
email_service = EmailService()

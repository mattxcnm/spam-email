#!/usr/bin/env python3
"""
Email Reporter - Send reports to authorities and companies
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime


class EmailReporter:
    """Class to handle sending reports via email"""
    
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file):
        """Load email configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def create_spam_report_email(self, spam_metadata, original_email_path=None):
        """Create a properly formatted spam report email"""
        
        msg = MIMEMultipart()
        msg['Subject'] = f"Spam Report - {spam_metadata.get('subject', 'Unknown Subject')}"
        
        # Create the email body
        body = f"""
Spam Email Report
================

Original Email Details:
- Subject: {spam_metadata.get('subject', 'N/A')}
- From: {spam_metadata.get('from', 'N/A')}
- Date: {spam_metadata.get('date', 'N/A')}
- Sender Domain: {spam_metadata.get('sender_domain', 'N/A')}
- Message ID: {spam_metadata.get('message_id', 'N/A')}
- Return Path: {spam_metadata.get('return_path', 'N/A')}

Analysis:
- Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Classification: Unsolicited Commercial Email (Spam)

Please investigate this email for potential violations of anti-spam regulations.

Received Headers:
{chr(10).join(spam_metadata.get('received', []))}

Additional Information:
This report was generated automatically as part of spam email processing.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach original email if available
        if original_email_path and Path(original_email_path).exists():
            with open(original_email_path, 'rb') as f:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename=spam_email_{datetime.now().strftime("%Y%m%d_%H%M%S")}.eml'
                )
                msg.attach(attachment)
        
        return msg
    
    def send_report_email(self, to_email, spam_metadata, original_email_path=None):
        """Send spam report email"""
        
        email_config = self.config.get('email_settings', {})
        
        if not all([email_config.get('smtp_server'), email_config.get('username'), 
                   email_config.get('password'), email_config.get('from_email')]):
            print("Email configuration incomplete. Please update config.json")
            return False
        
        try:
            msg = self.create_spam_report_email(spam_metadata, original_email_path)
            msg['From'] = email_config['from_email']
            msg['To'] = to_email
            
            # Connect to SMTP server
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(email_config['from_email'], to_email, text)
            server.quit()
            
            print(f"Successfully sent report to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_company_reports(self, actions_log_file):
        """Send reports to companies based on actions log"""
        
        try:
            with open(actions_log_file, 'r') as f:
                actions_data = json.load(f)
            
            # Load corresponding metadata
            timestamp = Path(actions_log_file).stem.replace("actions_taken_", "")
            metadata_file = Path(actions_log_file).parent / f"email_metadata_{timestamp}.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                spam_metadata = metadata.get('metadata', {})
                original_file = metadata.get('file_path', '')
                
                # Send to company contacts
                company_reports = actions_data.get('company_reports', [])
                for report in company_reports:
                    company_email = report.get('email')
                    if company_email:
                        self.send_report_email(company_email, spam_metadata, original_file)
                
        except Exception as e:
            print(f"Error sending company reports: {e}")
    
    def send_authority_reports(self, actions_log_file):
        """Send reports to authorities (where email is supported)"""
        
        # APWG accepts email reports
        apwg_email = "reportphishing@apwg.org"
        
        try:
            with open(actions_log_file, 'r') as f:
                actions_data = json.load(f)
            
            # Load corresponding metadata
            timestamp = Path(actions_log_file).stem.replace("actions_taken_", "")
            metadata_file = Path(actions_log_file).parent / f"email_metadata_{timestamp}.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                spam_metadata = metadata.get('metadata', {})
                original_file = metadata.get('file_path', '')
                
                # Send to APWG
                self.send_report_email(apwg_email, spam_metadata, original_file)
                
        except Exception as e:
            print(f"Error sending authority reports: {e}")


def main():
    """Main function for email reporter"""
    reporter = EmailReporter()
    
    print("Email Reporter for Spam Processing")
    print("==================================")
    
    # Find recent action logs
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("No logs directory found")
        return
    
    action_files = list(logs_dir.glob("actions_taken_*.json"))
    
    if not action_files:
        print("No action log files found")
        return
    
    print(f"Found {len(action_files)} action log files")
    
    choice = input("Send reports? (y/n): ").strip().lower()
    
    if choice == 'y':
        for action_file in action_files:
            print(f"Processing {action_file.name}...")
            reporter.send_company_reports(action_file)
            reporter.send_authority_reports(action_file)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Utility script to convert Apple Mail messages to .eml format
This helps with extracting emails from Apple Mail for processing
"""

import os
import sys
import sqlite3
import email
from pathlib import Path
from datetime import datetime


def find_mail_database():
    """Find the Apple Mail database location"""
    home = Path.home()
    mail_db_paths = [
        home / "Library" / "Mail" / "V10" / "MailData" / "Envelope Index",
        home / "Library" / "Mail" / "V9" / "MailData" / "Envelope Index",
        home / "Library" / "Mail" / "V8" / "MailData" / "Envelope Index",
    ]
    
    for path in mail_db_paths:
        if path.exists():
            return path
    
    return None


def extract_recent_emails(output_dir="consume", days_back=7):
    """Extract recent emails from Apple Mail database"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    mail_db = find_mail_database()
    if not mail_db:
        print("Could not find Apple Mail database")
        return
    
    try:
        conn = sqlite3.connect(str(mail_db))
        cursor = conn.cursor()
        
        # Query for recent emails (this is a simplified example)
        # The actual schema may vary between macOS versions
        query = """
        SELECT ROWID, subject, sender, date_received 
        FROM messages 
        WHERE date_received > ? 
        ORDER BY date_received DESC
        """
        
        # Calculate timestamp for days_back
        cutoff_time = datetime.now().timestamp() - (days_back * 24 * 60 * 60)
        
        cursor.execute(query, (cutoff_time,))
        results = cursor.fetchall()
        
        print(f"Found {len(results)} recent emails")
        
        # Note: This is a simplified extraction
        # Full implementation would require parsing the actual email files
        # from the Mail directory structure
        
        conn.close()
        
    except Exception as e:
        print(f"Error accessing Mail database: {e}")
        print("You may need to give Python permission to access Mail data")


def convert_msg_to_eml(msg_file, output_dir="consume"):
    """Convert a .msg file to .eml format"""
    # This would require the extract-msg library for full implementation
    # For now, just copy the file if it's already in email format
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    msg_path = Path(msg_file)
    output_file = output_path / f"{msg_path.stem}.eml"
    
    try:
        with open(msg_path, 'rb') as src:
            content = src.read()
            
        # Try to parse as email first
        try:
            email_msg = email.message_from_bytes(content)
            with open(output_file, 'wb') as dst:
                dst.write(content)
            print(f"Converted {msg_file} to {output_file}")
        except:
            print(f"Could not parse {msg_file} as email format")
            
    except Exception as e:
        print(f"Error converting {msg_file}: {e}")


if __name__ == "__main__":
    print("Apple Mail Email Extractor")
    print("==========================")
    print("This script helps extract emails from Apple Mail for spam processing")
    print()
    print("Options:")
    print("1. Extract recent emails from Mail database")
    print("2. Convert .msg file to .eml format")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        days = input("Enter number of days back to extract (default 7): ").strip()
        days = int(days) if days.isdigit() else 7
        extract_recent_emails(days_back=days)
    elif choice == "2":
        msg_file = input("Enter path to .msg file: ").strip()
        if os.path.exists(msg_file):
            convert_msg_to_eml(msg_file)
        else:
            print("File not found")
    else:
        print("Invalid choice")

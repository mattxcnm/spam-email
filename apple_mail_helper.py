#!/usr/bin/env python3
"""
Apple Mail Helper Script
Provides instructions and helpers for extracting spam emails from Apple Mail
"""

import os
import subprocess
from pathlib import Path


def show_apple_mail_instructions():
    """Show detailed instructions for extracting emails from Apple Mail"""
    
    instructions = """
Apple Mail Spam Extraction Guide
================================

Method 1: Manual Export (Recommended)
-------------------------------------
1. Open Apple Mail
2. Select the spam emails you want to process
3. Right-click on the selected emails
4. Choose "Save As..." from the context menu
5. In the save dialog:
   - Choose Format: "Raw Message Source"
   - This will save as .eml files
6. Save the files to the 'consume' directory in this project
7. Run: python3 spam-email.py

Method 2: Forward as Attachment
------------------------------
1. Select spam emails in Apple Mail
2. Choose "Message" → "Forward as Attachment"
3. Save the forwarded message as .eml format
4. Place in 'consume' directory

Method 3: Drag and Drop (macOS)
------------------------------
1. Open Finder and navigate to the consume directory
2. Open Apple Mail
3. Select spam emails
4. Drag the emails from Apple Mail to the Finder window
5. This should create .eml files automatically

Tips for Better Results:
-----------------------
- Process emails soon after receiving them (headers are fresher)
- Include the full email with headers for better analysis
- Don't modify the email content before processing
- Process different types of spam to build a comprehensive database

Security Notes:
--------------
- Only process emails you're certain are spam
- The tool will attempt to visit unsubscribe links (use caution)
- Review logs before sending any reports
- Consider using a separate network for processing if concerned about security

Troubleshooting:
---------------
- If emails don't save as .eml, try "Raw Message Source" format
- Check file permissions in the consume directory
- Ensure emails contain proper headers (From, To, Subject, etc.)
"""
    
    print(instructions)


def check_apple_mail_running():
    """Check if Apple Mail is currently running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'Mail.app'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def get_mail_directory_info():
    """Get information about Apple Mail directories"""
    home = Path.home()
    mail_dirs = [
        home / "Library" / "Mail",
        home / "Library" / "Mail" / "V10",
        home / "Library" / "Mail" / "V9",
        home / "Library" / "Mail" / "V8",
    ]
    
    print("Apple Mail Directory Information:")
    print("================================")
    
    for mail_dir in mail_dirs:
        if mail_dir.exists():
            print(f"✓ Found: {mail_dir}")
            
            # Check for MailData
            maildata = mail_dir / "MailData"
            if maildata.exists():
                print(f"  - MailData: {maildata}")
                
                # Check for database
                envelope_index = maildata / "Envelope Index"
                if envelope_index.exists():
                    print(f"  - Database: {envelope_index}")
        else:
            print(f"✗ Not found: {mail_dir}")
    
    print()


def create_automator_workflow():
    """Create an Automator workflow for easier email extraction"""
    
    workflow_content = '''
Automator Workflow for Spam Email Extraction
===========================================

To create an Automator workflow for easier spam processing:

1. Open Automator
2. Create a new "Quick Action" workflow
3. Set "Workflow receives" to "files or folders" in "Mail"
4. Add "Copy Finder Items" action:
   - Set destination to your spam-email/consume directory
5. Add "Run Shell Script" action:
   - Shell: /bin/bash
   - Pass input: as arguments
   - Script content:
   
   cd /path/to/your/spam-email
   python3 spam-email.py
   
6. Save the workflow with a name like "Process Spam Emails"

This will add a context menu option in Apple Mail to automatically
copy selected emails to the consume directory and process them.
'''
    
    print(workflow_content)


def main():
    """Main function for Apple Mail helper"""
    
    print("Apple Mail Integration Helper")
    print("============================")
    print()
    
    if check_apple_mail_running():
        print("✓ Apple Mail is currently running")
    else:
        print("✗ Apple Mail is not running")
    
    print()
    
    # Show mail directory info
    get_mail_directory_info()
    
    print("Choose an option:")
    print("1. Show manual extraction instructions")
    print("2. Show Automator workflow setup")
    print("3. Check consume directory")
    print("4. Exit")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        show_apple_mail_instructions()
    elif choice == "2":
        create_automator_workflow()
    elif choice == "3":
        consume_dir = Path("consume")
        if consume_dir.exists():
            files = list(consume_dir.glob("*.eml")) + list(consume_dir.glob("*.msg"))
            print(f"Found {len(files)} email files in consume directory:")
            for file in files:
                print(f"  - {file.name}")
        else:
            print("Consume directory not found")
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()

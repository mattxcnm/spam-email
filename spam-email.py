#!/usr/bin/env python3
"""
Spam Email Processing Tool
Processes spam emails by:
1. Attempting to unsubscribe
2. Reporting to authorities
3. Performing WHOIS lookups
4. Logging all actions
"""

import os
import re
import json
import email
import logging
import smtplib
import requests
import whois
import tldextract
from datetime import datetime
from pathlib import Path
from email import header
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import dns.resolver


class SpamEmailProcessor:
    """Main class for processing spam emails"""
    
    def __init__(self, consume_dir="consume", logs_dir="logs", processed_dir="processed"):
        self.consume_dir = Path(consume_dir)
        self.logs_dir = Path(logs_dir)
        self.processed_dir = Path(processed_dir)
        
        # Ensure directories exist
        self.consume_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Known company spam reporting endpoints
        self.company_reporting = {
            "paypal": "spoof@paypal.com",
            "amazon": "stop-spoofing@amazon.com",
            "apple": "reportphishing@apple.com",
            "microsoft": "phish@office365.microsoft.com",
            "google": "phishing@gmail.com",
            "facebook": "phish@fb.com",
            "ebay": "spoof@ebay.com",
            "netflix": "phishing@netflix.com",
            "ups": "fraud@ups.com",
            "fedex": "abuse@fedex.com",
            "wells fargo": "reportfraud@wellsfargo.com",
            "chase": "abuse@chase.com",
            "bank of america": "abuse@bankofamerica.com",
        }
        
        # Common unsubscribe text patterns
        self.unsubscribe_patterns = [
            r'unsubscribe',
            r'opt[- ]?out',
            r'remove.*list',
            r'stop.*email',
            r'click.*here.*remove',
            r'update.*preferences',
            r'manage.*subscription'
        ]
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs_dir / f"spam_processor_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def decode_mime_words(self, text):
        """Decode MIME encoded words in email headers"""
        if not text:
            return ""
        
        decoded_parts = decode_header(text)
        decoded_text = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_text += part.decode(encoding)
                else:
                    decoded_text += part.decode('utf-8', errors='ignore')
            else:
                decoded_text += str(part)
        
        return decoded_text
    
    def extract_email_metadata(self, email_msg):
        """Extract metadata from email message"""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "subject": self.decode_mime_words(email_msg.get("Subject", "")),
            "from": self.decode_mime_words(email_msg.get("From", "")),
            "to": self.decode_mime_words(email_msg.get("To", "")),
            "date": email_msg.get("Date", ""),
            "message_id": email_msg.get("Message-ID", ""),
            "return_path": email_msg.get("Return-Path", ""),
            "received": email_msg.get_all("Received", []),
            "x_mailer": email_msg.get("X-Mailer", ""),
            "x_originating_ip": email_msg.get("X-Originating-IP", ""),
        }
        
        # Extract sender domain
        from_email = metadata["from"]
        if "@" in from_email:
            domain_match = re.search(r'@([a-zA-Z0-9.-]+)', from_email)
            if domain_match:
                metadata["sender_domain"] = domain_match.group(1)
        
        return metadata
    
    def extract_email_content(self, email_msg):
        """Extract text and HTML content from email"""
        text_content = ""
        html_content = ""
        
        if email_msg.is_multipart():
            for part in email_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            text_content += payload.decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_content += payload.decode('utf-8', errors='ignore')
        else:
            payload = email_msg.get_payload(decode=True)
            if payload:
                content_type = email_msg.get_content_type()
                if content_type == "text/html":
                    html_content = payload.decode('utf-8', errors='ignore')
                else:
                    text_content = payload.decode('utf-8', errors='ignore')
        
        return text_content, html_content
    
    def find_unsubscribe_links(self, text_content, html_content):
        """Find unsubscribe links in email content"""
        unsubscribe_links = []
        
        # Check List-Unsubscribe header (RFC standard)
        # This would be handled in the main processing function
        
        # Find unsubscribe links in HTML content
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                link_text = link.get_text().lower()
                link_href = link['href']
                
                for pattern in self.unsubscribe_patterns:
                    if re.search(pattern, link_text, re.IGNORECASE):
                        unsubscribe_links.append(link_href)
                        break
        
        # Find unsubscribe links in plain text
        if text_content:
            url_pattern = r'https?://[^\s<>"\']+(?:unsubscribe|opt-?out|remove)[^\s<>"\']*'
            text_urls = re.findall(url_pattern, text_content, re.IGNORECASE)
            unsubscribe_links.extend(text_urls)
        
        return list(set(unsubscribe_links))  # Remove duplicates
    
    def attempt_unsubscribe(self, unsubscribe_links, email_metadata):
        """Attempt to unsubscribe from email lists"""
        unsubscribe_results = []
        
        for link in unsubscribe_links:
            try:
                # Simple GET request to unsubscribe link
                response = requests.get(link, timeout=10, allow_redirects=True)
                
                result = {
                    "link": link,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_url": response.url,
                    "timestamp": datetime.now().isoformat()
                }
                
                unsubscribe_results.append(result)
                self.logger.info(f"Unsubscribe attempt: {link} - Status: {response.status_code}")
                
            except Exception as e:
                result = {
                    "link": link,
                    "error": str(e),
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
                unsubscribe_results.append(result)
                self.logger.error(f"Unsubscribe failed for {link}: {str(e)}")
        
        return unsubscribe_results
    
    def perform_whois_lookup(self, domain):
        """Perform WHOIS lookup for domain"""
        try:
            w = whois.whois(domain)
            
            whois_data = {
                "domain": domain,
                "registrar": w.registrar,
                "creation_date": str(w.creation_date) if w.creation_date else None,
                "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                "name_servers": w.name_servers if w.name_servers else [],
                "emails": w.emails if w.emails else [],
                "org": w.org,
                "country": w.country,
                "timestamp": datetime.now().isoformat()
            }
            
            return whois_data
            
        except Exception as e:
            self.logger.error(f"WHOIS lookup failed for {domain}: {str(e)}")
            return {"domain": domain, "error": str(e), "timestamp": datetime.now().isoformat()}
    
    def identify_company_from_content(self, text_content, html_content, metadata):
        """Identify company names mentioned in email content"""
        identified_companies = []
        
        all_content = f"{text_content} {html_content} {metadata.get('subject', '')} {metadata.get('from', '')}"
        all_content_lower = all_content.lower()
        
        for company in self.company_reporting.keys():
            if company in all_content_lower:
                identified_companies.append(company)
        
        return identified_companies
    
    def report_to_authorities(self, email_metadata, email_content):
        """Report spam email to various authorities"""
        reports = []
        
        # FTC Spam reporting (US)
        ftc_report = {
            "authority": "FTC",
            "method": "Online Form",
            "url": "https://reportfraud.ftc.gov/",
            "status": "Manual submission required",
            "timestamp": datetime.now().isoformat()
        }
        reports.append(ftc_report)
        
        # IC3 (FBI Internet Crime Complaint Center)
        ic3_report = {
            "authority": "IC3",
            "method": "Online Form", 
            "url": "https://www.ic3.gov/Home/FileComplaint",
            "status": "Manual submission required",
            "timestamp": datetime.now().isoformat()
        }
        reports.append(ic3_report)
        
        # Anti-Phishing Working Group
        apwg_report = {
            "authority": "APWG",
            "method": "Email",
            "email": "reportphishing@apwg.org",
            "status": "Ready for email submission",
            "timestamp": datetime.now().isoformat()
        }
        reports.append(apwg_report)
        
        return reports
    
    def report_to_companies(self, identified_companies, email_metadata, email_content):
        """Report to specific companies being impersonated"""
        company_reports = []
        
        for company in identified_companies:
            if company in self.company_reporting:
                report = {
                    "company": company,
                    "email": self.company_reporting[company],
                    "status": "Ready for email submission",
                    "timestamp": datetime.now().isoformat()
                }
                company_reports.append(report)
        
        return company_reports
    
    def process_email_file(self, email_file_path):
        """Process a single email file"""
        self.logger.info(f"Processing email file: {email_file_path}")
        
        try:
            # Read and parse email
            with open(email_file_path, 'rb') as f:
                email_msg = email.message_from_bytes(f.read())
            
            # Extract metadata and content
            metadata = self.extract_email_metadata(email_msg)
            text_content, html_content = self.extract_email_content(email_msg)
            
            # Check for List-Unsubscribe header
            list_unsubscribe = email_msg.get("List-Unsubscribe", "")
            if list_unsubscribe:
                metadata["list_unsubscribe"] = list_unsubscribe
            
            # Find unsubscribe links
            unsubscribe_links = self.find_unsubscribe_links(text_content, html_content)
            if list_unsubscribe:
                # Extract URLs from List-Unsubscribe header
                list_unsub_urls = re.findall(r'<(https?://[^>]+)>', list_unsubscribe)
                unsubscribe_links.extend(list_unsub_urls)
            
            # Attempt unsubscribe
            unsubscribe_results = []
            if unsubscribe_links:
                unsubscribe_results = self.attempt_unsubscribe(unsubscribe_links, metadata)
            
            # WHOIS lookup
            whois_data = None
            if metadata.get("sender_domain"):
                whois_data = self.perform_whois_lookup(metadata["sender_domain"])
            
            # Identify companies
            identified_companies = self.identify_company_from_content(text_content, html_content, metadata)
            
            # Report to authorities
            authority_reports = self.report_to_authorities(metadata, {"text": text_content, "html": html_content})
            
            # Report to companies
            company_reports = self.report_to_companies(identified_companies, metadata, {"text": text_content, "html": html_content})
            
            # Compile results
            processing_results = {
                "file_path": str(email_file_path),
                "metadata": metadata,
                "unsubscribe_links": unsubscribe_links,
                "unsubscribe_results": unsubscribe_results,
                "whois_data": whois_data,
                "identified_companies": identified_companies,
                "authority_reports": authority_reports,
                "company_reports": company_reports,
                "processing_timestamp": datetime.now().isoformat()
            }
            
            # Log results
            self.log_processing_results(processing_results)
            
            # Move processed file
            processed_file_path = self.processed_dir / email_file_path.name
            email_file_path.rename(processed_file_path)
            
            self.logger.info(f"Successfully processed {email_file_path.name}")
            return processing_results
            
        except Exception as e:
            self.logger.error(f"Error processing {email_file_path}: {str(e)}")
            return None
    
    def log_processing_results(self, results):
        """Log processing results to JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Email metadata log
        metadata_log_file = self.logs_dir / f"email_metadata_{timestamp}.json"
        with open(metadata_log_file, 'w') as f:
            json.dump({
                "file_path": results["file_path"],
                "metadata": results["metadata"],
                "whois_data": results["whois_data"],
                "processing_timestamp": results["processing_timestamp"]
            }, f, indent=2)
        
        # Actions log
        actions_log_file = self.logs_dir / f"actions_taken_{timestamp}.json"
        with open(actions_log_file, 'w') as f:
            json.dump({
                "file_path": results["file_path"],
                "unsubscribe_attempts": results["unsubscribe_results"],
                "authority_reports": results["authority_reports"],
                "company_reports": results["company_reports"],
                "processing_timestamp": results["processing_timestamp"]
            }, f, indent=2)
    
    def process_all_emails(self):
        """Process all email files in the consume directory"""
        email_files = list(self.consume_dir.glob("*.eml")) + list(self.consume_dir.glob("*.msg"))
        
        if not email_files:
            self.logger.info("No email files found in consume directory")
            return
        
        self.logger.info(f"Found {len(email_files)} email files to process")
        
        for email_file in email_files:
            self.process_email_file(email_file)
    
    def generate_summary_report(self):
        """Generate a summary report of all processed emails"""
        log_files = list(self.logs_dir.glob("email_metadata_*.json"))
        
        if not log_files:
            self.logger.info("No processed emails found for summary")
            return
        
        summary = {
            "total_emails_processed": len(log_files),
            "processing_date": datetime.now().isoformat(),
            "domains_encountered": [],
            "companies_identified": [],
            "total_unsubscribe_attempts": 0,
            "successful_unsubscribes": 0
        }
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                
                # Collect domain info
                if data.get("metadata", {}).get("sender_domain"):
                    domain = data["metadata"]["sender_domain"]
                    if domain not in summary["domains_encountered"]:
                        summary["domains_encountered"].append(domain)
                
                # Look for corresponding actions file
                timestamp = log_file.stem.replace("email_metadata_", "")
                actions_file = self.logs_dir / f"actions_taken_{timestamp}.json"
                
                if actions_file.exists():
                    with open(actions_file, 'r') as af:
                        actions_data = json.load(af)
                    
                    # Count unsubscribe attempts
                    unsub_attempts = actions_data.get("unsubscribe_attempts", [])
                    summary["total_unsubscribe_attempts"] += len(unsub_attempts)
                    summary["successful_unsubscribes"] += sum(1 for attempt in unsub_attempts if attempt.get("success"))
                    
                    # Collect company reports
                    company_reports = actions_data.get("company_reports", [])
                    for report in company_reports:
                        company = report.get("company")
                        if company and company not in summary["companies_identified"]:
                            summary["companies_identified"].append(company)
            
            except Exception as e:
                self.logger.error(f"Error reading log file {log_file}: {str(e)}")
        
        # Save summary report
        summary_file = self.logs_dir / f"summary_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Summary report saved to {summary_file}")
        return summary


def main():
    """Main function to run the spam email processor"""
    processor = SpamEmailProcessor()
    
    print("Spam Email Processor")
    print("===================")
    print("Place email files (.eml or .msg) in the 'consume' directory")
    print("The tool will:")
    print("1. Attempt to unsubscribe from emails")
    print("2. Report emails to authorities")
    print("3. Perform WHOIS lookups")
    print("4. Generate detailed logs")
    print()
    
    # Process all emails
    processor.process_all_emails()
    
    # Generate summary report
    summary = processor.generate_summary_report()
    
    if summary:
        print(f"Processing complete!")
        print(f"Total emails processed: {summary['total_emails_processed']}")
        print(f"Unsubscribe attempts: {summary['total_unsubscribe_attempts']}")
        print(f"Successful unsubscribes: {summary['successful_unsubscribes']}")
        print(f"Unique domains: {len(summary['domains_encountered'])}")
        print(f"Companies identified: {len(summary['companies_identified'])}")


if __name__ == "__main__":
    main()
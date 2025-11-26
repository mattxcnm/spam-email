# Spam Email Processing Tool

A comprehensive tool for processing spam emails to help combat the spam problem. This tool automatically processes spam emails by attempting to unsubscribe, reporting to authorities, performing WHOIS lookups, and maintaining detailed logs.

## Features

### Core Functionality
- **Automatic Unsubscribe**: Finds and follows unsubscribe links (including RFC-compliant List-Unsubscribe headers)
- **Authority Reporting**: Reports spam to FTC, IC3, and APWG
- **Company Reporting**: Identifies impersonated companies and reports to their abuse contacts
- **WHOIS Analysis**: Performs domain analysis for sender domains
- **Comprehensive Logging**: Tracks all actions and maintains detailed metadata

### Supported Email Formats
- `.eml` files (standard email format)
- `.msg` files (Outlook format)

## Directory Structure

```
spam-email/
├── consume/           # Place email files here for processing
├── processed/         # Processed emails are moved here
├── logs/             # Detailed logs of all processing
├── spam-email.py     # Main processing script
├── email_reporter.py # Email reporting utility
├── extract_emails.py # Apple Mail extraction helper
├── config.json       # Configuration file
└── requirements.txt  # Python dependencies
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Usage
1. Copy spam email files (`.eml` or `.msg`) to the `consume/` directory
2. Run the processor:
   ```bash
   python spam-email.py
   ```
3. Check the `logs/` directory for detailed results

### Apple Mail Integration
If you're using Apple Mail on macOS:

1. **Manual Method**: 
   - Select spam emails in Apple Mail
   - Right-click → "Save As..." → Choose "Raw Message Source" format
   - Save as `.eml` files to the `consume/` directory

2. **Helper Script** (experimental):
   ```bash
   python extract_emails.py
   ```

## Configuration

Edit `config.json` to customize settings:

```json
{
  "email_settings": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com", 
    "password": "your-app-password",
    "from_email": "your-email@gmail.com"
  },
  "reporting_settings": {
    "enable_auto_unsubscribe": true,
    "enable_authority_reporting": true,
    "enable_company_reporting": true,
    "max_unsubscribe_attempts": 3,
    "request_timeout": 10
  }
}
```

## What the Tool Does

### 1. Email Analysis
- Extracts metadata (sender, subject, dates, headers)
- Parses email content (text and HTML)
- Identifies sender domain

### 2. Unsubscribe Attempts
- Finds unsubscribe links in email content
- Checks RFC-compliant List-Unsubscribe headers
- Attempts to unsubscribe via HTTP requests
- Logs all attempts and results

### 3. WHOIS Lookup
- Performs domain registration lookup
- Extracts registrar information
- Identifies abuse contacts
- Logs domain ownership details

### 4. Company Identification
- Scans content for known company names
- Matches against database of company abuse contacts
- Prepares reports for impersonated companies

### 5. Authority Reporting
Prepares reports for:
- **FTC** (Federal Trade Commission)
- **IC3** (FBI Internet Crime Complaint Center)  
- **APWG** (Anti-Phishing Working Group)

### 6. Company Reporting
Built-in contacts for major companies:
- PayPal, Amazon, Apple, Microsoft
- Google, Facebook, eBay, Netflix
- UPS, FedEx, Wells Fargo, Chase
- Bank of America, and more

## Logging and Reports

### Email Metadata Logs
Detailed information about each processed email:
- `logs/email_metadata_YYYYMMDD_HHMMSS.json`

### Actions Taken Logs
Record of all actions performed:
- `logs/actions_taken_YYYYMMDD_HHMMSS.json`

### Summary Reports
Daily summary of processing activity:
- `logs/summary_report_YYYYMMDD.json`

## Advanced Usage

### Email Reporting
Send reports via email to companies and authorities:

```bash
python email_reporter.py
```

This requires email configuration in `config.json`.

### Bulk Processing
Process multiple emails at once by placing them all in the `consume/` directory and running the main script.

### Custom Company Contacts
Add custom company abuse contacts in `config.json`:

```json
{
  "additional_company_contacts": {
    "example-company": "abuse@example.com",
    "another-company": "security@company.com"
  }
}
```

## Safety and Legal Considerations

### Unsubscribe Safety
- Only attempts unsubscribe for legitimate-looking links
- Uses timeouts to prevent hanging
- Logs all attempts for review

### Reporting Ethics
- Only reports actual spam/phishing emails
- Includes proper context in reports
- Follows established reporting procedures

### Privacy
- All processing is done locally
- No email content is sent to external services (except for reporting)
- Logs can be reviewed before any reports are sent

## Troubleshooting

### Common Issues

1. **Import Errors**: Install missing dependencies with `pip install -r requirements.txt`

2. **Permission Errors**: Ensure the script has write access to the logs and processed directories

3. **Email Format Issues**: Ensure emails are saved in `.eml` format from your email client

4. **Network Timeouts**: Adjust timeout settings in `config.json`

### Debug Mode
Add logging verbosity by modifying the logging level in `spam-email.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

This tool is designed to help combat spam email. Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Ideas for Enhancement
- Additional email format support
- More authority reporting endpoints
- Machine learning spam classification
- GUI interface
- Integration with email clients

## Legal Notice

This tool is designed for processing emails you have received. Always comply with:
- Local laws regarding email processing
- Terms of service of reporting organizations
- Privacy regulations in your jurisdiction

Use responsibly and only for legitimate spam fighting purposes.

## License

This project is open source. Please use it responsibly to help combat spam email.

---

**Remember**: The goal is to help reduce spam email for everyone. Use this tool responsibly and in accordance with all applicable laws and regulations.
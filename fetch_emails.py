import os
import json
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def decode_mime_header(header_value):
    """Decode MIME-encoded email headers (e.g. =?UTF-8?B?...?=)."""
    if not header_value:
        return ''
    decoded_parts = decode_header(header_value)
    parts = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                parts.append(part.decode(charset or 'utf-8', errors='replace'))
            except (LookupError, UnicodeDecodeError):
                parts.append(part.decode('utf-8', errors='replace'))
        else:
            parts.append(str(part))
    return ' '.join(parts)


def extract_links(soup):
    """Extract all http/https links from BeautifulSoup parsed HTML."""
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(strip=True) or href
        if href.startswith(('http://', 'https://')):
            links.append({'url': href, 'text': text})
    return links


def get_body_and_links(msg):
    """Extract plain text body and all hyperlinks from an email message."""
    body_text = ''
    all_links = []

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue

            try:
                content = payload.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                content = payload.decode('latin-1', errors='replace')

            content_type = part.get_content_type()

            if content_type == 'text/html':
                soup = BeautifulSoup(content, 'html.parser')
                body_text = soup.get_text(separator='\n', strip=True)
                all_links = extract_links(soup)
                break
            elif content_type == 'text/plain' and not body_text:
                body_text = content
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            try:
                content = payload.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                content = payload.decode('latin-1', errors='replace')

            content_type = msg.get_content_type()
            if content_type == 'text/html':
                soup = BeautifulSoup(content, 'html.parser')
                body_text = soup.get_text(separator='\n', strip=True)
                all_links = extract_links(soup)
            else:
                body_text = content

    return body_text, all_links


def main():
    load_dotenv()

    HOST = os.getenv('EMAIL_HOST')
    USER = os.getenv('EMAIL_USER')
    PASS = os.getenv('EMAIL_PASS')

    if not all([HOST, USER, PASS]):
        print("Error: Missing email configuration in .env (EMAIL_HOST, EMAIL_USER, EMAIL_PASS)")
        return

    print(f"Connecting to {HOST}...")
    mail = imaplib.IMAP4_SSL(HOST)
    mail.login(USER, PASS)

    # Send IMAP ID command (required by 163.com to avoid 'Unsafe Login' block)
    imaplib.Commands['ID'] = ('AUTH',)
    imap_id = ('name', 'claude-code', 'contact', USER, 'version', '1.0.0', 'os', 'python')
    id_args = "(" + " ".join(f'"{x}"' for x in imap_id) + ")"
    mail._simple_command('ID', id_args)

    mail.select('INBOX')

    since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
    print(f"Searching for unread emails since {since_date}...")

    status, messages = mail.search(None, f'(UNSEEN SINCE {since_date})')
    if status != 'OK' or not messages[0]:
        print("No unread emails found in the last 7 days.")
        results = []
    else:
        email_nums = messages[0].split()
        print(f"Total unread: {len(email_nums)}. Filtering for sender containing 'pitchbook'...")

        results = []
        for i, num in enumerate(email_nums, 1):
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue

            # Parse the raw email bytes
            raw_email = None
            for part in data:
                if isinstance(part, tuple):
                    raw_email = part[1]
                    break
            if raw_email is None:
                continue

            msg = email.message_from_bytes(raw_email)

            sender = msg.get('From', '')
            if 'pitchbook' not in sender.lower():
                continue

            subject = decode_mime_header(msg['Subject'])
            date = msg.get('Date', '')

            body_text, all_links = get_body_and_links(msg)

            report_keywords = ['download', 'report', 'pdf']
            report_links = [
                link for link in all_links
                if any(kw in link['url'].lower() or kw in link['text'].lower() for kw in report_keywords)
            ]

            results.append({
                'subject': subject,
                'date': date,
                'sender': sender,
                'body_text': body_text,
                'report_links': report_links,
                'all_links': all_links,
            })

            mail.store(num, '+FLAGS', '\\Seen')
            print(f"  [{i}/{len(email_nums)}] Processed: {subject[:70]}")

    os.makedirs('data', exist_ok=True)
    with open('data/emails.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(results)} email(s) saved to data/emails.json")
    mail.logout()


if __name__ == '__main__':
    main()

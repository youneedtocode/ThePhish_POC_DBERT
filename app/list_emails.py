import logging.config
import imaplib
import json
import email
import base64
import traceback
import bs4
import magic

# Global variable used for logging
log = None

# Global variable used for the configuration
config = {}

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['thephish']
verdicts_collection = db['verdicts']

def connect_to_IMAP_server():
    connection = imaplib.IMAP4_SSL(config['imapHost'], config['imapPort'])
    connection.login(config['imapUser'], config['imapPassword'])
    log.info('Connected to {0}@{1}:{2}/{3}'.format(config['imapUser'], config['imapHost'], config['imapPort'], config['imapFolder']))
    return connection

def retrieve_emails(connection):
    connection.select(config['imapFolder'])
    typ, dat = connection.search(None, 'ALL')
    all_ids = dat[0].split()
    last_20_ids = all_ids[-20:] if len(all_ids) > 20 else all_ids
    print("DEBUG: IMAP search returned:", last_20_ids)
    
    log.info("{} most recent messages to process".format(len(last_20_ids)))


    emails_info = []
    
    for num in reversed(last_20_ids):
        msg_uid = num.decode()

        typ, dat = connection.fetch(num, '(RFC822)')
        if typ != 'OK':
            log.error(dat[-1])
        message = dat[0][1]

        connection.store(num, '-FLAGS', '\\Seen')

        msg = email.message_from_bytes(message)
        decode = email.header.decode_header(msg['From'])[-1]
        from_field = decode[0].decode(decode[1]) if decode[1] else str(decode[0])
        decode = email.header.decode_header(msg['Subject'])[-1]
        subject_field = decode[0].decode(decode[1]) if decode[1] else str(decode[0])
        log.info("Message from: {0} with subject: {1}".format(from_field, subject_field))

        body = None
        eml_attachment_found = False
        is_there_text = False

        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                is_there_text = True
            elif part.get_content_type() == "message/rfc822":
                break

        attached_mail_subject = ''

        for part in msg.walk():
            mimetype = part.get_content_type()
            if mimetype in ['application/octet-stream', 'message/rfc822']:
                if mimetype == 'application/octet-stream':
                    eml_payload = part.get_payload(decode=1)
                    internal_msg = email.message_from_bytes(eml_payload)
                    if magic.from_buffer(eml_payload, mime=True) not in ['text/plain', 'message/rfc822']:
                        continue
                elif mimetype == 'message/rfc822':
                    eml_payload = part.get_payload(decode=0)[0]
                    try:
                        internal_msg = email.message_from_string(base64.b64decode(str(eml_payload)).decode()) 
                    except:
                        internal_msg = eml_payload

                eml_attachment_found = True

                decode = email.header.decode_header(internal_msg['Subject'])
                decoded_elements = []
                for decode_elem in decode:
                    if decode_elem[1]:
                        decoded_elements.append(decode_elem[0].decode(decode_elem[1]))
                    else:
                        decoded_elements.append(str(decode_elem[0]) if isinstance(decode_elem[0], str) else decode_elem[0].decode())
                attached_mail_subject = ''.join(decoded_elements)
                log.info("Found attached mail with subject: {0} ({1})".format(attached_mail_subject, mimetype))
                break

            elif mimetype == "multipart/mixed":
                if not is_there_text:
                    part_payload = part.get_payload()[0]
                    is_there_text_in_multipart = False
                    for subpart in part_payload.walk():
                        if subpart.get_content_type() == "text/plain":
                            is_there_text_in_multipart = True
                    for subpart in part_payload.walk():
                        if subpart.get_content_type() == "text/plain" and not body:
                            try:
                                body = subpart.get_payload(decode=True).decode()
                            except UnicodeDecodeError:
                                body = subpart.get_payload(decode=True).decode('ISO-8859-1')
                        elif subpart.get_content_type() == "text/html" and not is_there_text_in_multipart and not body:
                            try:
                                html = subpart.get_payload(decode=True).decode()
                            except UnicodeDecodeError:
                                html = subpart.get_payload(decode=True).decode('ISO-8859-1')
                            soup = bs4.BeautifulSoup(html, 'html.parser')
                            body = soup.get_text()
            elif mimetype == "text/plain" and is_there_text:
                if not body:
                    try:
                        body = part.get_payload(decode=True).decode()
                    except UnicodeDecodeError:
                        body = part.get_payload(decode=True).decode('ISO-8859-1')
            elif mimetype == "text/html":
                try:
                    html = part.get_payload(decode=True).decode()
                except UnicodeDecodeError:
                    html = part.get_payload(decode=True).decode('ISO-8859-1')
                if not body:
                    soup = bs4.BeautifulSoup(html, 'html.parser')
                    body = soup.get_text()

        # ✅ No condition — include all emails
        email_info = {
            'mailUID': num.decode(),
            'from': from_field,
            'subject': subject_field,
            'date': msg['Date'],
            'body': body,
            'attachedMail': attached_mail_subject if eml_attachment_found else "N/A"
        }

        for key in email_info:
            email_info[key] = email_info[key].encode("unicode-escape").decode().replace(r'\x92', '\'').encode().decode("unicode-escape")
        
        # Check MongoDB for existing verdict
        verdict_doc = verdicts_collection.find_one({"mail_uid": msg_uid})
        if verdict_doc and "verdict" in verdict_doc:
            email_info["verdict"] = verdict_doc["verdict"]
        else:
            email_info["verdict"] = None

        emails_info.append(email_info)

    return emails_info

def main():
    global config
    global log

    try:
        with open('logging_conf.json') as log_conf:
            log_conf_dict = json.load(log_conf)
            logging.config.dictConfig(log_conf_dict)
    except Exception as e: 
        print("[ERROR]_[list_emails]: Error while trying to open the file 'logging_conf.json': {}".format(traceback.format_exc()))
        return 
    log = logging.getLogger(__name__)

    try:
        with open('configuration.json') as conf_file:
            conf_dict = json.load(conf_file)
            config['imapHost'] = conf_dict['imap']['host']
            config['imapPort'] = int(conf_dict['imap']['port'])
            config['imapUser'] = conf_dict['imap']['user']
            config['imapPassword'] = conf_dict['imap']['password']
            config['imapFolder'] = conf_dict['imap']['folder']
    except Exception as e: 
        log.error("Error while trying to open the file 'configuration.json': {}".format(traceback.format_exc()))
        return

    try:
        connection = connect_to_IMAP_server()
    except Exception as e:
        log.error("Error while trying to connect to IMAP server: {}".format(traceback.format_exc()))
        return

    try:
        emails_info = retrieve_emails(connection)
    except Exception as e:
        log.error("Error while trying to retrieve the emails: {}".format(traceback.format_exc()))
        return

    return emails_info


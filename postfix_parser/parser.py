import re
import os


class LogFileDoesNotExist(Exception):
    pass


class PostfixParser(object):
    email_id_rex = 'postfix.+? ([0-9A-F]+):'
    email_sender_rex = 'sasl_username=([^,\s]+)'
    email_removed_rex = ': removed$'
    email_status_rex = 'to=<(.*?)>.*?status=(\w+)'

    def __init__(self, filename):
        if not os.path.exists(filename):
            raise LogFileDoesNotExist()

        self.filename = filename
        self.__buffer = {}
        self.__stats = {}

    def __rex_first(self, regex, text):
        result = re.findall(regex, text)
        if result:
            return result[0]

    def __extract_email_sender_to_buffer(self, email_id, line):
        sender_email = self.__rex_first(self.email_sender_rex, line)
        if sender_email:
            self.__buffer[email_id] = {
                'sender': sender_email, 'success': set(), 'error': set()
            }

    def __extract_email_reciever_to_buffer(self, email_id, line):
        email_reciever_status = self.__rex_first(self.email_status_rex, line)
        if email_reciever_status and email_id in self.__buffer:
            email_reciever, email_status = email_reciever_status

            if email_status == 'sent':
                self.__buffer[email_id]['success'].add(email_reciever)
                self.__buffer[email_id]['error'].discard(email_reciever)
            else:
                self.__buffer[email_id]['error'].add(email_reciever)

    def __extract_sender_stats(self, email_id, line):
        if re.search(self.email_removed_rex, line) and email_id in self.__buffer:
            email = self.__buffer[email_id]
            sender_email = email['sender']

            stats = self.__stats.get(sender_email, {'success': 0, 'error': 0})
            stats['success'] += len(email['success'])
            stats['error'] += len(email['error'])
            self.__stats[sender_email] = stats

    def __parse_log(self):
        with open(self.filename, 'r') as f:
            for line in f:
                email_id = self.__rex_first(self.email_id_rex, line)
                if email_id is None:
                    continue

                self.__extract_email_sender_to_buffer(email_id, line)
                self.__extract_email_reciever_to_buffer(email_id, line)
                self.__extract_sender_stats(email_id, line)

    def __reset_stats(self):
        self.__stats = {}
        self.__buffer = {}

    def get_mail_stats(self):
        self.__reset_stats()
        self.__parse_log()
        return self.__stats

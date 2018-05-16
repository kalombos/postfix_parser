import re
import os


class LogFileDoesNotExist(Exception):
    pass


class PostfixParser(object):
    email_id_rex = 'postfix.+? ([0-9A-F]+):'
    email_sender_rex = 'sasl_username=(.+)$'
    email_removed_rex = ': removed$'
    email_status_rex = 'to=<(.*?)>.*?status=(\w+)'

    def __init__(self, filename):
        if not os.path.exists(filename):
            raise LogFileDoesNotExist()

        self.filename = filename
        self.__buffer = {}

    def __rex_first(self, regex, text):
        result = re.findall(regex, text)
        if result:
            return result[0]

    def __process_email_sender(self, email_id, line):
        sender_email = self.__rex_first(self.email_sender_rex, line)
        if sender_email:
            self.__buffer[email_id] = {
                'sender': sender_email, 'success': set(), 'error': set()
            }

    def __process_email_reciever(self, email_id, line):
        email_reciever_status = self.__rex_first(self.email_status_rex, line)
        if email_reciever_status:
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
            return {sender_email: {
                'success': len(email['success']), 'error': len(email['error'])
            }}

    def get_mail_stats(self):

        stats = {}
        with open(self.filename, 'r') as f:
            for line in f:
                email_id = self.__rex_first(self.email_id_rex, line)
                if email_id is None:
                    continue

                self.__process_email_sender(email_id, line)

                self.__process_email_reciever(email_id, line)
                sender_stats = self.__extract_sender_stats(email_id, line)
                if sender_stats:
                    stats.update(sender_stats)
        return stats
    #
    # def parse_log(self):
    #     pass
    #
    # def process_mail(self, mail_id):
    #     self.stats[mail_id] = MailAnalyzer(self.data[mail_id]).stats()
    #     del self.data[mail_id]
    #
    # def run(self):
    #     with open(self.filename) as f:
    #         for line in f:
    #             res = re.findall(self.mail_id_rex, line)
    #             if not res:
    #                 continue
    #             mail_id = res[0]
    #             # For test
    #             if mail_id != '451CEDF04EB':
    #                 continue
    #             if mail_id not in self.data:
    #                 self.data[mail_id] = []
    #
    #             self.data[mail_id].append(line)
    #             if re.search(self.mail_removed_rex, line):
    #                 self.process_mail(mail_id)
    #     print(self.stats)


# class MailAnalyzer(object):
#
#     # TODO: check for space
#     auth_rex = 'sasl_username=(.+)$'
#     status_rex = 'to=.*?delay=.*?status=(\w+)'
#
#     def __init__(self, lines):
#         self.lines = lines
#
#     def detect_sender(self):
#         pass
#
#     def stats(self):
#         data = {'success': 0, 'error': 0}
#         for line in self.lines:
#             if 'mail' not in data:
#                 res = re.findall(self.auth_rex, line)
#                 if res:
#                     data['mail'] = res[0]
#                     continue
#             res = re.findall(self.status_rex, line)
#             if not res:
#                 continue
#             status = res[0]
#             if status == 'sent':
#                 data['success'] += 1
#             else:
#                 data['error'] += 1
#         return data

#PostfixParser(FILENAME).run()



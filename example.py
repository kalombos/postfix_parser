# -*- coding: utf-8 -*-

from postfix_parser.parser import PostfixParser

stats = PostfixParser('postfix.log').get_mail_stats()
for email, report in stats.items():
    print(
        'From <%s> was sent %s emails successfully, %s ones have errors and was not sent' %
        (email, report['success'], report['error'])
    )

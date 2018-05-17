# postfix_parser

### Description
There is tool to get report from postfix log file about emails that was sent.
### How to use
```
from postfix_parser.parser import PostfixParser

stats = PostfixParser('postfix.log').get_mail_stats()
for email, report in stats.items():
    print(
        'From <%s> was sent %s emails successfully, %s ones have errors and was not sent' %
        (email, report['success'], report['error'])
    )

    
>>>From <import5@fmgifts.ru> was sent 3 emails successfully, 0 ones have errors and was not sent
>>>From <a.melnikov@soyuz-group.ru> was sent 1 emails successfully, 0 ones have errors and was not sent
>>>From <pc@scan-avia.ru> was sent 3 emails successfully, 2 ones have errors and was not sent

....

```
### How to run unittests
```
pip install -r requirements_dev.txt
nosetests

```


import unittest
from app.parser import PostfixParser, LogFileDoesNotExist
import tempfile


class PostfixParserTestCase(unittest.TestCase):

    mail1 = "mail1@test.ru"
    mail2 = "mail2@test.ru"
    should_not_exists_mail = "should_not_exists@test.ru"

    def test_pass_file_that_does_not_exist(self):
        self.assertRaises(LogFileDoesNotExist, PostfixParser, 'not_exist_file.log')

    def create_tmp_log(self, text):
        filename = tempfile.mkstemp()[1]

        with open(filename, 'w') as f:
            f.write(text)
        return filename

    def test_empty_file_mail_stats_method(self):
        filename = self.create_tmp_log('')
        parser = PostfixParser(filename)
        self.assertEqual(parser.get_mail_stats(), {})

    def test_get_mail_stats_method_1_email(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=%s" % self.mail1,
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 25E6CDF04F4: removed"
        ]))

        parser = PostfixParser(filename)
        self.assertEqual(parser.get_mail_stats(), {self.mail1: {'success': 0, 'error': 0}})

    def test_get_mail_stats_method_2_email(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=%s" % self.mail1,
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 25E6CDF04F4: removed",
            "postfix/qmgr[3043]: 33333333333: sasl_username=%s" % self.mail2,
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 33333333333: removed"
        ]))

        parser = PostfixParser(filename)
        self.assertEqual(
            parser.get_mail_stats(),
            {
                self.mail1: {'success': 0, 'error': 0},
                self.mail2: {'success': 0, 'error': 0}
            }
        )

    def test_mail_log_should_have_uid(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=should_exists@test.ru",
            "sasl_username=%s" % self.should_not_exists_mail,
        ]))

        parser = PostfixParser(filename)
        self.assertNotIn(self.should_not_exists_mail,  parser.get_mail_stats().keys())

    def test_mail_should_count_when_it_is_removed(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=should_exists@test.ru",
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 25E6CDF04F4: removed",
            "postfix/qmgr[3043]: 33333333333: sasl_username=%s" % self.should_not_exists_mail,
        ]))

        parser = PostfixParser(filename)
        self.assertNotIn(self.should_not_exists_mail, parser.get_mail_stats().keys())

    def test_success_email_was_sent(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=%s" % self.mail1,
            "postfix/smtp[23225]: 25E6CDF04F4: to=<arsenal@scn.ru>, status=sent (250 OK)",
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 25E6CDF04F4: removed",
        ]))

        parser = PostfixParser(filename)
        self.assertEqual(parser.get_mail_stats(), {self.mail1: {'success': 1, 'error': 0}})

    def test_success_email_was_sent_but_had_errors(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=%s" % self.mail1,
            "postfix/smtp[23225]: 25E6CDF04F4: to=<arsenal@scn.ru>, status=deferred",
            "postfix/smtp[23225]: 25E6CDF04F4: to=<arsenal@scn.ru>, status=sent",
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 25E6CDF04F4: removed",
        ]))

        parser = PostfixParser(filename)
        self.assertEqual(parser.get_mail_stats(), {self.mail1: {'success': 1, 'error': 0}})

    def test_email_has_error(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=%s" % self.mail1,
            "postfix/smtp[23225]: 25E6CDF04F4: to=<arsenal@scn.ru>, status=bounced",
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 25E6CDF04F4: removed",
        ]))

        parser = PostfixParser(filename)
        self.assertEqual(parser.get_mail_stats(), {self.mail1: {'success': 0, 'error': 1}})

    def test_1_email_has_error_1_email_is_sent(self):
        filename = self.create_tmp_log('\n'.join([
            "postfix/qmgr[3043]: 25E6CDF04F4: sasl_username=%s" % self.mail1,
            "postfix/smtp[23225]: 25E6CDF04F4: to=<mail2@test.ru>, status=bounced",
            "postfix/smtp[23225]: 25E6CDF04F4: to=<mail1@test.ru>, status=sent",
            "Jul 10 10:09:09 srv24-s-st postfix/qmgr[3043]: 25E6CDF04F4: removed",
        ]))

        parser = PostfixParser(filename)
        self.assertEqual(parser.get_mail_stats(), {self.mail1: {'success': 1, 'error': 1}})
    # def test_get_mail_stats_method_2_email(self):
    #     filename = tempfile.mkstemp()[1]
    #
    #     with open(filename, 'w') as f:
    #         f.write(
    #             """Jul 10 10:09:10 srv24-s-st postfix/smtpd[27068]:
    #             451CEDF04EB: client=unknown[213.87.122.107], sasl_method=LOGIN,
    #             sasl_username=manager30@moda-milena.ru""")
    #
    #     parser = PostfixParser(filename)
    #     self.assertEqual(parser.get_mail_stats(), {'manager30@moda-milena.ru': {}})



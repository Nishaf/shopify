import os
import sys
import logging
import datetime
import queue


class LoggingProvider:

    class __LoggingProvider:
        use_print = True

        def __init__(self, log_file_path=None, use_print=True):
            self.messages = queue.Queue()
            self.use_print = use_print
            logs_dir = os.path.join(sys.path[0], 'logs')
            #if not os.path.exists(logs_dir):
            #    os.makedirs(logs_dir)
            if not log_file_path:
                now_date = datetime.datetime.now().strftime("%b%d%Y%I%M%p")
                log_file_name = 'scraper_%s.logs' % now_date
                log_file_path = os.path.join(logs_dir, log_file_name.lower())
            self.full_file_path = os.path.normpath(log_file_path)
            logging.basicConfig(filename=log_file_path, filemode='w', level=logging.DEBUG)

        def critical(self, msg=None, args=None, kwargs=None):
            self.print_log(msg)
            logging.critical(msg=msg)

        def warning(self, msg=None, args=None, kwargs=None):
            self.print_log(msg)
            logging.warning(msg=msg)

        def info(self, msg=None, args=None, kwargs=None):
            self.print_log(msg)
            logging.info(msg=msg)

        def print_log(self, msg):
            self.messages.put((msg, ))
            if self.use_print:
                print(msg)

        def get_messages(self):
            messages = ""
            while not self.messages.empty():
                messages += '\n' + self.messages.get()[0]
            return messages

        def has_messages(self):
            return not self.messages.empty()

    instance = None

    def __init__(self, log_file_path=None, use_print=True):
        if not LoggingProvider.instance:
            LoggingProvider.instance = LoggingProvider.__LoggingProvider(log_file_path, use_print=use_print)

    def critical(self, msg=None, args=None, kwargs=None):
        LoggingProvider.instance.critical(msg=msg)

    def warning(self, msg=None, args=None, kwargs=None):
        LoggingProvider.instance.warning(msg=msg)

    def info(self, msg=None, args=None, kwargs=None):
        LoggingProvider.instance.info(msg=msg)
    def has_messages(self):
        return LoggingProvider.instance.has_messages()
    def get_messages(self):
        return LoggingProvider.instance.get_messages()
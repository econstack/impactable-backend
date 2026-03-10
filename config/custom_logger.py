import logging
from pprint import pformat

LOG_LEVEL_GLOBAL = None


class CustomLogger(object):

    # _all_loggers = {}

    # @classmethod
    def getLogger(name, formatter=None, level=logging.INFO):
        """
        custom logger with default formatter and level=INFO. Calls should be of form: logger = CustomLogger.getLogger(
            name='service-name',
            formatter=logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
            )
        """
        # if not cls._all_loggers.get(name, None):

        l = logging.getLogger(name)
        handler = logging.StreamHandler()
        # putting in a bunch of diagnostic information
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        if not formatter:
            formatter = logging.Formatter(
                "%(levelname)s: %(asctime)s - %(name)s - %(filename)s.%(funcName)s:%(lineno)d  %(message)s"
            )
        handler.setFormatter(formatter)
        l.addHandler(handler)
        l.setLevel(level)
        # turn off propagation so that output to console only appears once
        l.propagate = False
        # cls._all_loggers[name] = l

        # return cls._all_loggers[name]
        return l


def df_log_formatter(df, nrows=2):
    """given df, logs shape, columns, head and tail"""
    if df is not None:
        msg = f"shape(df):{df.shape} \n df.columns:\n{pformat(df.info())}, \nHEAD\n{df.head(nrows)}, \nTAIL\n{df.tail(nrows)}"
    else:
        msg = "[Empty Dataframe]"
    return msg

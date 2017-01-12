from datetime import datetime,timedelta


def segement_daterange(start, end, maxdelta):
    """
    Segments a date range into shorter pieces with 'maxdelta' length.
    :param start: starting datetime
    :param end:  ending datetime
    :param maxdelta: timedelta instance representing max time window
    :return:
    """

    cur = start
    while cur < end:
        yield (cur, min(cur + maxdelta, end))
        cur += maxdelta




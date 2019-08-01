import json
import logging
import sys
from typing import Dict, Optional, Set


class LoggerWithFlexibleArgs(logging.Logger):
    """
        This class just add content of **kwargs to 'data' key of the extra argument of LogRecord.
        This give ability to use any keyword argument in standard logging functions. This is very
        useful in structured logging goal because extra argument will be passed as is to
        a formatter. In conjunction with JsonFormatter this will result that the keyword arguments
        will appears in a JSON document in "data" key.
    """

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs):
        if extra is None:
            extra = {}
        extra = {**extra, **{'data': kwargs}}

        return super()._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info
        )


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        fmt=None,
        datefmt=None,
        style='%',
        skip_fields_calculation: Optional[Set[str]] = None,
        drop_fields_from_json: Optional[Set[str]] = None,
        simplify_exception_text: bool = True,
        json_dumps_args: Optional[Dict] = None,
    ):
        super().__init__(fmt, datefmt, style)
        self._skip_fields_calculation = set(skip_fields_calculation) if skip_fields_calculation \
            else set()
        self._drop_fields_from_json = set(drop_fields_from_json) if drop_fields_from_json else set()
        self._simplify_exception_text = bool(simplify_exception_text)
        self._json_dumps_args = json_dumps_args if json_dumps_args else {}

    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        if record.exc_info:
            record.exceptionClass = record.exc_info[0].__name__
            record.exceptionMessage = str(record.exc_info[1])
            # Cache the traceback text to avoid converting it multiple times (it's constant anyway)
            if not record.exc_text and 'exc_text' not in self._skip_fields_calculation:
                record.exc_text = self.formatException(record.exc_info)
        if 'messageFormatted' not in self._skip_fields_calculation:
            record.messageFormatted = self.formatMessage(record)

        data = record.__dict__

        del data['msg'], data['args']
        # We can't serialize exc_info to JSON be default thus drop it.
        del data['exc_info']

        for field in self._drop_fields_from_json:
            if field in data:
                del data[field]

        return json.dumps(data, **self._json_dumps_args)


def init_flexible_logger(name: str) -> logging.Logger:
    logger_class_backup = logging.getLoggerClass()
    try:
        # Unfortunately we can't acquire the lock from logging module here thus this temporary
        # change will affect any parallel loggers creation.
        logging.setLoggerClass(LoggerWithFlexibleArgs)
        return logging.getLogger(name)
    finally:
        logging.setLoggerClass(logger_class_backup)


def init_json_logger(
    name: str,
    drop_formatted_message: bool = True,
    drop_old_exception_text: bool = True,
    stream=sys.stdout,
    formatter: Optional[JsonFormatter] = None
) -> logging.Logger:
    if not formatter:
        skip_fields = set()
        if drop_formatted_message:
            skip_fields.add('messageFormatted')
        if drop_old_exception_text:
            skip_fields.add('exc_text')
        formatter = JsonFormatter(
            skip_fields_calculation=skip_fields,
            drop_fields_from_json=skip_fields
        )

    result = init_flexible_logger(name)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    result.addHandler(handler)

    return result

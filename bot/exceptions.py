"""
Bot Exceptions
~~~~~~~~~~~~~~

Exceptions handled by the bot.
"""


class OilAndRopeException(Exception):
    """
    Base class for exceptions.
    """

    def __init__(self, message, *, expire_in=0):
        super().__init__(message)
        self._message = message
        self.expire_in = expire_in

    @property
    def message(self):
        return self._message

    @property
    def message_no_format(self):
        return self._message


class CommandError(OilAndRopeException):
    """
    Exception raised when processing a command failed.
    """


class PermissionsError(OilAndRopeException):
    """
    Exception raised when no permissions to execute a command.
    """

    @property
    def message(self):
        return "You don't have permission to use that command.\nMore info: %(message)s" % {'message': self._message}


class HelpfulError(OilAndRopeException):
    """
    Error with format so the user can actually understand what the hell is going on.
    """

    def __init__(self, issue, solution, *, preface="An error ocurred", footnote="", expire_in=0):
        super(HelpfulError, self).__init__(issue, expire_in=expire_in)
        self.issue = issue
        self.solution = solution
        self.preface = preface
        self.footnote = footnote
        self.expire_in = expire_in
        self._message_fmt = "\n{preface}\n{problem}\n\n{solution}\n\n{footnote}"

    @property
    def message(self):
        return self._message_fmt.format(
            preface=self.preface,
            problem="\tProblem: %(problem)s" % {'problem': self.issue},
            solution="\tSolution: %(solution)s" % {'solution': self.solution},
            footnote=self.footnote
        )

    def __str__(self):
        return self.message


class HelpfulErrorWarning(HelpfulError):
    """
    Warning instead of error.
    """

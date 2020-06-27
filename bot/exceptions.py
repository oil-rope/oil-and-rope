from json import JSONDecodeError


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
        return f'You don\'t have permission to use that command.\nMore info: {self._message}'


class HelpfulError(OilAndRopeException):
    """
    Error with format so the user can actually understand what the hell is going on.
    """

    def __init__(self, issue, solution, *, preface="An error ocurred", footnote="", expire_in=0):
        super().__init__(issue, expire_in=expire_in)
        self.issue = issue
        self.solution = solution
        self.preface = preface
        self.footnote = footnote
        self.expire_in = expire_in
        self._message_fmt = '\n{preface}\n{problem}\n\n{solution}\n\n{footnote}'

    @property
    def message(self):
        return self._message_fmt.format(
            preface=self.preface,
            problem=f'\tProblem: {self.issue}',
            solution=f'\tSolution: {self.solution}',
            footnote=self.footnote
        )

    def __str__(self):
        return self.message


class HelpfulErrorWarning(HelpfulError):
    """
    Warning instead of error.
    """


class DiscordApiException(HelpfulError):
    """
    Handles error to give a possible solution.
    """

    def __init__(self, response):
        self.response = response
        self.handle_error_code(self.response)
        super().__init__(issue=self.issue, solution=self.solution, preface=self.preface, footnote=self.footnote)

    def handle_error_code(self, response):
        try:
            msg = response.json()['message']
        except JSONDecodeError:
            msg = f'Impossible to format response as JSON.\n{response.text}'
        self.error_code = response.status_code
        self.preface = f'[{response.status_code}] {msg}'

        if self.error_code == 400:
            self.issue = f'Bad Request [{self.error_code}]'
            self.solution = 'Maybe your data is bad formatted or you are trying to perform a forbidden action.'
            self.footnote = 'Please note that a bot cannot interact with itself.'
        elif self.error_code == 401:
            self.issue = f'Unauthorized [{self.error_code}]'
            self.solution = 'Maybe you are trying to connect a user that is not sharing server with our bot.'
            self.footnote = 'Please note that user and bot must share at least one server.'
        elif self.error_code == 403:
            self.issue = f'Forbidden [{self.error_code}]'
            self.solution = 'This action is forbidden. Maybe you need permissions?'
            self.footnote = ''
        elif self.error_code == 404:
            self.issue = f'Not found [{self.error_code}]'
            self.solution = 'The resource you are looking for does not exist. Is URL correct?'
            self.footnote = ''
        else:
            self.issue = f'Error [{self.error_code}]'
            self.solution = ''
            self.footnote = ''

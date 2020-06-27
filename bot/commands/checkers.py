from distutils.dist import strtobool as to_bool


def is_author(author):
    """
    Checks if givne author is the same who sent the message.
    """

    def check(m):
        return m.author == author
    return check


def is_yes_or_no():
    """
    Checks if the author's response is affirmative.
    """

    def check(m):
        try:
            # strtobool returns 0 or 1, here we make sure answer are yes, no, n, y, true, false...
            result = to_bool(m.content)
            result = result in (0, 1)
            return result
        # If value is something unexpected strtobool throws ValueError
        except ValueError:
            return False
    return check


def answer_in_list(item_list):
    """
    Checks if the given answer is in the list.
    """

    def check(m):
        result = m.content in item_list
        return result
    return check


def multiple_checks(*args):
    """
    Returns the result of multiple checks.
    """

    def check(m):
        final_result = all(func(m) for func in args)
        return final_result
    return check

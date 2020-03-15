def validate(*validations):
    """
    Checks if all `validations` are correct before executing.
    """

    def message_validation(func):
        def func_wrapper(*args, **kwargs):
            if all(validations):
                func(*args, **kwargs)
        return func_wrapper
    return message_validation

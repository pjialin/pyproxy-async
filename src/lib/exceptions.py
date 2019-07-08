class RetryException(Exception):
    pass


class MaxRetryException(Exception):
    pass


class ValidationFailException(Exception):
    pass


class EmptyResponseException(Exception):
    pass

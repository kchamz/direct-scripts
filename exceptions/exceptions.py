class DirectClientException(Exception):
    pass


class DNRClientException(Exception):
    pass


class UserLoginException(DirectClientException):
    pass


class ProposalCreateException(DirectClientException):
    pass


class EmbeddingException(DirectClientException):
    pass


class ProposalItemGetException(DirectClientException):
    pass


class ProposalGetException(DirectClientException):
    pass


class CorrelationIDNotFound(DirectClientException):
    pass

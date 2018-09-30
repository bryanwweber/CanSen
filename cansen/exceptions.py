"""Exceptions for CanSen."""


class CanSenError(Exception):
    """Base class for errors in CanSen."""

    pass


class KeywordError(CanSenError):
    """Raised for errors in keyword parsing."""

    def __init__(self, *keywords):
        self.keywords = keywords


class MultipleProblemError(KeywordError):
    """Raised error when multiple problem types are specified."""

    def __str__(self):
        return repr('Error: more than one problem type keyword was specified.'
                    '\n{key1} and {key2} were specified'.format(
                        key1=self.keywords[0], key2=self.keywords[1]))


class UnsupportedKeyword(Warning):
    """Raised error when a keyword is unsupported."""

    def __init__(self, *keywords):
        self.keywords = keywords

    def __str__(self):
        return repr('Warning: keyword(s) {key1} is not supported yet and '
                    'has been ignored'.format(key1=self.keywords))


class UndefinedKeywordError(KeywordError):
    """Raised for undefined keywords."""

    def __str__(self):
        return repr('Error: Keyword not defined.\n{}'.format(self.keywords))


class MissingReqdKeywordError(KeywordError):
    """Raised for missing required keywords."""

    def __str__(self):
        return repr('Error: Required keyword {} is missing.'.format(
            self.keywords))


class MissingKeyword(Warning):
    """Raised when an optional keyword is missing."""

    def __str__(self):
        return repr('Warning: {}'.format(self.args[0]))

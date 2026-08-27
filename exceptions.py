


class ParserError(Exception):
    pass


class NbDronesError(ParserError):
    pass

class StartHubError(ParserError):
    pass

class EndHubError(ParserError):
    pass

class HubError(ParserError):
    pass

class ConnectionError(ParserError):
    pass

class MetaDataError(ParserError):
    pass

class ValidationError(ParserError):
    pass
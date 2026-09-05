


class ParserError(Exception):
    """Base exception for parsing and syntax errors in the map file."""
    pass


class NbDronesError(ParserError):
    """Raised when the number of drones is invalid or missing."""
    pass


class StartHubError(ParserError):
    """Raised when the start hub configuration is invalid or missing."""
    pass


class EndHubError(ParserError):
    """Raised when the end hub configuration is invalid or missing."""
    pass


class HubError(ParserError):
    """Raised when a hub configuration or definition is invalid."""
    pass


class ConnectionError(ParserError):
    """Raised when a connection definition between hubs is invalid."""
    pass


class MetaDataError(ParserError):
    """Raised when metadata formatting or values are invalid."""
    pass


class ValidationError(ParserError):
    """Raised when map semantic validation fails."""
    pass
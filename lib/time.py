import time

__all__ = [ "to_hex" ]

def to_hex( seconds : int | float ) -> str :
    return hex( int( seconds ) )[ 2 : ]

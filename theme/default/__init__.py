"""
the default theme for simplog
"""

import lib.theme

__all__ = [ "theme" , "version" , "description" ]

class theme( lib.theme.theme ) :

    def __init__( self , path: str | None = None ) -> None :
        super().__init__( path )

__version__ = version = "0.0.1"
description = "the default theme for simplog"

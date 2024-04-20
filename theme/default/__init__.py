"""
the default theme for simplog
"""

import os

import lib.config
import lib.theme

__all__ = [ "theme" , "version" , "description" ]

class theme( lib.theme.theme ) :

    def __init__( self , path: str | None = None ) -> None :
        super().__init__( path )
        self.path_source = os.path.join( self.path , "source" )

    def init( self ) -> None :
        self.config_set()

    def config_set( self ) -> lib.config.parser :
        with lib.config.parser( os.path.join( self.path_source , "config" , "theme.json" ) , check_exist = False ) as config :
            config.add( "giscus" , {
                "src" : "https://giscus.app/client.js",
                "async" : None
            } )
            config.add( "mistune_plugins" , [
                "math",
                "strikethrough",
                "footnotes",
                "table",
                "task_lists",
                "abbr",
                "mark",
                "insert",
                "superscript",
                "subscript"
            ] )
        return config

    def main( self ) -> None :
        self.config = self.config_set()

    def build( self ) -> None :
        pass

    def post( self , path : str , title : str ) -> None :
        pass

    def page( self , path : str , title : str ) -> None :
        pass

__version__ = version = "0.0.1"
description = "the default theme for simplog"

"""
the default theme for simplog
"""

import mistune.plugins
import langful
import mistune
import sys
import os

import lib.config
import lib.theme
import lib.path

sys.path.insert( 0 , os.path.dirname( __file__ ) )

import renderer

sys.path.pop( 0 )

__all__ = [ "theme" , "version" , "description" ]

class theme( lib.theme.theme ) :

    def __init__( self , path: str | None = None ) -> None :
        super().__init__( path )
        self.path_source = os.path.join( self.path , "source" )

    def init( self ) -> None :
        self.set_config()

    def main( self ) -> None :
        self.lang = langful.langful( os.path.join( os.path.dirname( __file__ ) , "lang" ) )
        self.config = self.set_config()
        self.markdown = mistune.Markdown( renderer.HTMLRenderer( False ) , plugins = [ mistune.plugins.import_plugin( plugin ) for plugin in self.config.get( "mistune_plugins" ) ] )

    def set_config( self ) -> lib.config.parser :
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

    def set_config_info( self , path : str ) -> lib.config.parser :
        with lib.config.parser( os.path.join( path , "info.json" ) , False ) as config :
            pass
        return config

    def set_config_page( self , path : str ) -> lib.config.parser :
        with lib.config.parser( os.path.join( path , "page.json" ) , False ) as config :
            pass
        return config

    def build( self ) -> None :
        pass

    def post( self , path : str , title : str ) -> None :
        lib.path.checkfile( os.path.join( path , "index.md" ) )

    def page( self , path : str , title : str ) -> None :
        lib.path.checkfile( os.path.join( path , title + ".md" ) )
        self.set_config_info( path )
        self.set_config_page( path )

__version__ = version = "0.0.1"
description = "the default theme for simplog"
requirement = os.path.join( os.path.dirname( __file__ ) , "requirements.txt" )

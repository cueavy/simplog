import http.server
import argparse
import langful
import shutil
import typing
import types
import http
import time
import re
import os

import lib.config
import lib.theme
import lib.path

__all__ = [ "ArgumentParser" , "formatname" ]

home = os.path.dirname( __file__ )
config_default = {
    "theme" : "default",
    "output" : "output",
    "blacklist" : [
        ".git",
    ]
}

class ArgumentParser( argparse.ArgumentParser ) :

    def __init__( self , prog : str , description : str , help : str , lang : langful.langful , **kwargs : typing.Any ) -> None :
        super().__init__( lang.get( prog ) , description = lang.get( description ) , add_help = False , **kwargs )
        self.add_argument( "-h" , "--help" , action = "help" , help = lang.get( help ) )
        self.lang = lang

def formatname( name : str ) -> str :
    name = name.strip()
    if name and name[ 0 ] == "." : name = name[ 1 : ]
    if name and name[ -1 ] == "." : name = name[ : -1 ]
    name = name.replace( " " , "-" )
    name = re.sub( """[<>:"/\\|?*]""" , "_" ,  name )
    return name[ : 255 ]

if __name__ == "__main__" :
    lang = langful.langful( os.path.join( home , "lang" ) )
    parser = ArgumentParser( "parser.name", "parser.description" , "help.help" , lang )
    parser.add_argument( "-i" , "--init" , required = False , action = "store_true" , help = lang.get( "help.init" ) )
    parser.add_argument( "--theme" , required = False , default = "default" , help = lang.get( "help.theme" ) )
    parser.add_argument( "-l" , "--list" , required = False , action = "store_true" , help = lang.get( "help.theme.list" ) )
    parser.add_argument( "-s" , "--server" , required = False , action = "store_true" , help = lang.get( "help.server" ) )
    parser.add_argument( "--port" , required = False , default = 7000 , type = int , help = lang.get( "help.server.port" ) )
    parser.add_argument( "-c" , "--clear" , required = False , action = "store_true" , help = lang.get( "help.clear" ) )
    parser.add_argument( "-b" , "--build" , required = False , action = "store_true" , help = lang.get( "help.build" ) )
    parser.add_argument( "-p" , "--post" , required = False , default = None , type = str , help = lang.get( "help.post" ) )
    parser.add_argument( "--page" , required = False , default = None , type = str , help = lang.get( "help.page" ) )
    args = parser.parse_args()
    if args.init :
        # load theme
        theme_name = args.theme
        if not os.path.isdir( path := os.path.join( home , "theme" , theme_name ) ) :
            print( lang.get( "theme.error.not_exist" ) )
            exit()
        try :
            theme = lib.theme.theme_load( path )
        except ImportError :
            print( lang.get( "theme.error.load_failed" ) )
            exit()
        print( lang.replace( "init.theme" , { "name" : theme_name } ) )
        # create and copy files
        if os.path.isdir( "source" ) :
            if len( os.listdir( "source" ) ) :
                print( lang.get( "init.error.source_exist" ) )
                exit()
            else : os.rmdir( "source" )
        theme_path = os.path.dirname( str( theme.__file__ ) )
        path = os.path.join( theme_path , "source" )
        if os.path.isdir( path ) :
            shutil.copytree( path , "source" )
        else :
            print( lang.get( "init.warning.theme_no_source_dir" ) )
            os.mkdir( "source" )
        [ os.mkdir( path ) for path in ( os.path.join( "source" , path ) for path in [ "asset" , "config" , "post" , "page" , "template" ] ) if not os.path.exists( path ) ]
        # config
        with lib.config.parser( os.path.join( "source" , "config" , "config.json" ) , check_exist = False ) as config :
            config.add_all( config_default )
            config.set( "theme" , theme_name )
        # theme init
        theme_main : lib.theme.theme = theme.theme()
        theme_main.init()
        print( lang.get( "init.done" ) )
        exit()
    if args.list :
        themes : dict[ str , types.ModuleType ] = {}
        for name in os.listdir( os.path.join( home , "theme" ) ) :
            try : themes[ name ] = lib.theme.theme_load( os.path.join( home , "theme" , name ) )
            except : continue
        if len( themes ) :
            print( lang.get( "list.list" ) )
            for name , theme in themes.items() :
                print( " " * 2 , name , f" - ({ theme.version })" if hasattr( theme , "version" ) else "" , f" : { theme.description }" if hasattr( theme , "description" ) else "" , sep = "" )
        else :
            print( lang.get( "list.empty" ) )
        exit()
    if not os.path.exists( "source" ) :
        print( lang.get( "error.source_not_exist" ) )
        exit()
    try :
        config = lib.config.parser( os.path.join( "source" , "config" , "config.json" ) )
        config.add_all( config_default )
    except :
        print( lang.get( "error.load_config" ) )
        exit()
    output_path = config.get( "output" )
    if not os.path.exists( output_path ) : os.makedirs( output_path )
    if args.server :
        httpd = http.server.HTTPServer( ( "0.0.0.0" , port := args.port ) , http.server.SimpleHTTPRequestHandler )
        print( f"http://0.0.0.0{ f':{ port if port != 80 else '' }' }" )
        os.chdir( output_path )
        try : httpd.serve_forever()
        except KeyboardInterrupt : ...
    if args.clear or args.build :
        lib.path.rmtree( output_path , config.get( "blacklist" ) )
        if not args.build : exit()
    theme_name = config.get( "theme" )
    try :
        theme : types.ModuleType = lib.theme.theme_load( os.path.join( home , "theme" , theme_name ) )
        theme_class : lib.theme.theme = theme.theme()
    except :
        print( lang.get( "theme.error.load_failed" ) )
        exit()
    theme_class.main()
    if args.build :
        theme_class.build()
        exit()
    if args.post :
        time_create = time.time()
        os.makedirs( os.path.join( "source" , "post" , *( time.strftime( "%Y|%m-%d" , time.localtime( time_create ) ) ).split( "|" ) ) )
        exit()
    if args.page :
        time_create = time.time()
        os.makedirs( os.path.join( "source" , "page" , formatname( args.page ) ) )
        exit()

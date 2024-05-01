import http.server
import subprocess
import threading
import traceback
import argparse
import langful
import shutil
import typing
import types
import http
import time
import sys
import os

import lib.config
import lib.theme
import lib.path

__all__ = [ "ArgumentParser" ]

home = os.path.dirname( __file__ )

def load_config( check_exist : bool = True ) -> lib.config.parser :
    with lib.config.parser( os.path.join( "source" , "config" , "config.json" ) , check_exist ) as config :
        config.add( "theme" , "default" )
        config.add( "output" , "output" )
        config.add( "blacklist" , [ ".git" ] )
    return config

class ArgumentParser( argparse.ArgumentParser ) :

    def __init__( self , prog : str , description : str , help : str , lang : langful.langful , **kwargs : typing.Any ) -> None :
        super().__init__( lang.get( prog ) , description = lang.get( description ) , add_help = False , **kwargs )
        self.add_argument( "-h" , "--help" , action = "help" , help = lang.get( help ) )
        self.lang = lang

if __name__ == "__main__" :
    lang = langful.langful( os.path.join( home , "lang" ) )
    parser = ArgumentParser( "parser.name", "parser.description" , "help.help" , lang )
    parser.add_argument( "-i" , "--init" , required = False , action = "store_true" , help = lang.get( "help.init" ) )
    parser.add_argument( "-f" , "--force" , required = False , action = "store_true" , help = lang.get( "help.force" ) )
    parser.add_argument( "-t" , "--theme" , required = False , default = "default" , help = lang.get( "help.theme" ) )
    parser.add_argument( "-l" , "--list" , required = False , action = "store_true" , help = lang.get( "help.theme.list" ) )
    parser.add_argument( "-s" , "--server" , required = False , action = "store_true" , help = lang.get( "help.server" ) )
    parser.add_argument( "-p" , "--port" , required = False , default = 7000 , type = int , help = lang.get( "help.server.port" ) )
    parser.add_argument( "-c" , "--clear" , required = False , action = "store_true" , help = lang.get( "help.clear" ) )
    parser.add_argument( "-b" , "--build" , required = False , action = "store_true" , help = lang.get( "help.build" ) )
    parser.add_argument( "--post" , required = False , default = None , type = str , help = lang.get( "help.post" ) )
    parser.add_argument( "--page" , required = False , default = None , type = str , help = lang.get( "help.page" ) )
    args = parser.parse_args()
    # init
    if args.init :
        # load theme
        theme_name = args.theme
        force = args.force
        if not os.path.isdir( path := os.path.join( home , "theme" , theme_name ) ) :
            print( lang.get( "theme.error.not_exist" ) )
            exit()
        try :
            theme = lib.theme.theme_load( path )
        except ImportError :
            traceback.print_exc()
            print( lang.get( "theme.error.load_failed" ) )
            exit()
        print( lang.replace( "init.theme" , { "name" : theme_name } ) )
        # create and copy files
        if os.path.isdir( "source" ) :
            if len( os.listdir( "source" ) ) :
                if force :
                    print( lang.get( "init.info.force" ) )
                else :
                    print( lang.get( "init.error.source_exist" ) )
                    exit()
            else :
                os.rmdir( "source" )
        if os.path.isdir( path := os.path.join( os.path.dirname( str( theme.__file__ ) ) , "source" ) ) : shutil.copytree( path , "source" , dirs_exist_ok = True if force else False )
        else : print( lang.get( "init.warning.theme_no_source_dir" ) )
        [ os.makedirs( path ) for path in ( os.path.join( "source" , path ) for path in ( "asset" , "config" , "post" , "page" , "template" ) ) if not os.path.exists( path ) ]
        # config
        with load_config( False ) as config : config.set( "theme" , theme_name )
        # install requirement
        if hasattr( theme , "requirement" ) :
            print( lang.get( "init.requirement.start" ) )
            subprocess.check_call( [ sys.executable , "-m" , "pip" , "install" , "-r" , theme.requirement ] )
            print( lang.get( "init.requirement.done" ) )
        # theme init
        theme_main : lib.theme.theme = theme.theme()
        theme_main.init()
        print( lang.get( "init.done" ) )
        exit()
    # list
    if args.list :
        themes : dict[ str , types.ModuleType ] = {}
        for name in os.listdir( os.path.join( home , "theme" ) ) :
            try : 
                themes[ name ] = lib.theme.theme_load( os.path.join( home , "theme" , name ) )
            except :
                traceback.print_exc()
                print( lang.replace( "list.load_error" , { "name" : name } ) )
                continue
        if len( themes ) :
            print( lang.get( "list.list" ) )
            get_attr : typing.Callable[ [ types.ModuleType , str , str , str ] , str ] = lambda theme , text , attr , default = "" : text.replace( "{}" , getattr( theme , attr ) ) if hasattr( theme , attr ) else default
            [ print( " " * 2 , get_attr( theme , f"{{}} [{ name }]" , "name" , name ) , get_attr( theme , " - ({})" , "version" ) , get_attr( theme , " : {}" , "description" ) , sep = "" ) for name , theme in themes.items() ]
        else :
            print( lang.get( "list.empty" ) )
        exit()
    # load config
    if not os.path.exists( "source" ) :
        print( lang.get( "cli.error.source_not_exist" ) )
        exit()
    try :
        config = load_config()
    except :
        traceback.print_exc()
        print( lang.get( "cli.error.load_config" ) )
        exit()
    output_path = config.get( "output" )
    if not os.path.exists( output_path ) : os.makedirs( output_path )
    # server
    if args.server :
        with http.server.HTTPServer( ( "0.0.0.0" , port := args.port ) , http.server.SimpleHTTPRequestHandler ) as httpd :
            os.chdir( output_path )
            print( f"http://localhost{ f':{ port if port != 80 else '' }' }" )
            thread = threading.Thread( target = lambda : httpd.serve_forever() , daemon = True )
            thread.start()
            try : 
                while thread.is_alive() : thread.join( 0.1 )
            except KeyboardInterrupt :
                pass
        exit()
    # clear
    if args.clear or args.build :
        lib.path.rmtree( output_path , config.get( "blacklist" ) )
        if not args.build : exit()
    # load theme
    theme_name = config.get( "theme" )
    try :
        theme : types.ModuleType = lib.theme.theme_load( os.path.join( home , "theme" , theme_name ) )
        theme_class : lib.theme.theme = theme.theme()
    except :
        traceback.print_exc()
        print( lang.get( "theme.error.load_failed" ) )
        exit()
    theme_class.main()
    # build
    if args.build :
        theme_class.build( output_path )
        lib.path.copytree( os.path.join( "source" , "asset" ) , output_path )
        exit()
    # post
    if args.post :
        title : str = args.post
        time_create = time.time()
        path = os.path.join( "source" , "post" , *( time.strftime( "%Y|%m-%d" , time.localtime( time_create ) ) ).split( "|" ) , lib.path.formatname( title ) )
        try :
            lib.path.checkdir( path )
        except FileExistsError :
            print( lang.get( "post.error.exist" ) )
            exit()
        theme_class.post( path , title )
        exit()
    # page
    if args.page :
        title = args.page
        time_create = time.time()
        path = os.path.join( "source" , "page" , lib.path.formatname( title ) )
        try :
            os.makedirs( path )
        except FileExistsError :
            print( lang.get( "page.error.exist" ) )
            exit()
        theme_class.page( path , title )
        exit()

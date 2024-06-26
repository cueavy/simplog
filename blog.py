import http.server
import subprocess
import threading
import traceback
import argparse
import shutil
import typing
import types
import http
import time
import sys
import os

import langful

import lib.config
import lib.theme
import lib.path

__all__ = [ "load_config" ]

home = os.path.dirname( __file__ )

def load_config( check_exist : bool = True ) -> lib.config.parser :
    with lib.config.parser( os.path.join( "source" , "config" , "config.json" ) , check_exist ) as config :
        config.add( "theme" , "default" )
        config.add( "output" , "output" )
        config.add( "blacklist" , [ ".git" ] )
    return config

if __name__ == "__main__" :
    lang = langful.langful( os.path.join( home , "lang" ) )
    parser = argparse.ArgumentParser( lang.get( "parser.name" ) , description = lang.get( "parser.description" ) , add_help = False )
    parser.add_argument( "-h" , "--help" , action = "help" , help = lang.get( "help.help" ) )
    parser.add_argument( "-i" , "--init" , action = "store_true" , help = lang.get( "help.init" ) )
    parser.add_argument( "-t" , "--theme" ,  default = "default" , help = lang.get( "help.theme" ) )
    parser.add_argument( "-l" , "--list" , action = "store_true" , help = lang.get( "help.theme.list" ) )
    parser.add_argument( "-s" , "--server" , action = "store_true" , help = lang.get( "help.server" ) )
    parser.add_argument( "-p" , "--port" ,  default = 7000 , type = int , help = lang.get( "help.server.port" ) )
    parser.add_argument( "-c" , "--clear" , action = "store_true" , help = lang.get( "help.clear" ) )
    parser.add_argument( "-b" , "--build" , action = "store_true" , help = lang.get( "help.build" ) )
    parser.add_argument( "--post" ,  default = None , type = str , help = lang.get( "help.post" ) )
    parser.add_argument( "--page" ,  default = None , type = str , help = lang.get( "help.page" ) )
    args = parser.parse_args()
    # init
    if args.init :
        # load theme
        theme_name = args.theme
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
        # prepare environment
        if os.path.exists( "source" ) and len( os.listdir( "source" ) ) :
            print( lang.get( "init.error.source_exist" ) )
            exit()
        if os.path.exists( path := os.path.join( os.path.dirname( str( theme.__file__ ) ) , "source" ) ) :
            print( lang.get( "init.info.copy_source" ) )
            shutil.copytree( path , "source" , dirs_exist_ok = True )
        if not os.path.exists( "source" ) : os.mkdir( "source" )
        with load_config( False ) as config : config.set( "theme" , theme_name )
        [ os.mkdir( path ) for path in ( os.path.join( "source" , path ) for path in ( "asset" , "config" , "post" , "page" , "template" ) ) if not os.path.exists( path ) ]
        # install requirement
        if hasattr( theme , "requirement" ) :
            print( lang.get( "init.requirement.start" ) )
            subprocess.check_call( [ sys.executable , "-m" , "pip" , "install" , "-r" , theme.requirement ] )
            print( lang.get( "init.requirement.done" ) )
        # theme init
        theme_main : lib.theme.theme = theme.theme_class()
        theme_main.init()
        # done
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
                while thread.is_alive() : thread.join( 1 )
            except KeyboardInterrupt :
                pass
        exit()
    # clear
    if args.clear or args.build :
        lib.path.rmtree( output_path , config.get( "blacklist" ) )
        if args.clear : exit()
    # load theme
    theme_name = config.get( "theme" )
    try :
        theme : types.ModuleType = lib.theme.theme_load( os.path.join( home , "theme" , theme_name ) )
        theme_class : lib.theme.theme = theme.theme_class()
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
    # no argument
    parser.print_help()
    exit()

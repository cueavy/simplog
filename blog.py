import http.server
import argparse
import langful
import typing
import types
import http
import os

import lib.theme

__all__ = [ "ArgumentParser" ]

home = os.path.dirname( __file__ )

class ArgumentParser( argparse.ArgumentParser ) :

    def __init__( self , prog : str , description : str , help : str , lang : langful.langful , **kwargs : typing.Any ) -> None :
        super().__init__( lang.get( prog ) , description = lang.get( description ) , add_help = False , **kwargs )
        self.add_argument( "-h" , "--help" , action = "help" , help = lang.get( help ) )
        self.lang = lang

if __name__ == "__main__" :
    lang = langful.langful( os.path.join( home , "lang" ) )
    parser = ArgumentParser( "parser.name", "parser.description" , "help.help" , lang )
    parser.add_argument( "-i" , "--init" , required = False , action = "store_true" , help = lang.get( "help.init" ) )
    parser.add_argument( "--theme" , required = False , default = "default" , help = lang.get( "help.theme" ) )
    parser.add_argument( "-l" , "--list" , required = False , action = "store_true" , help = lang.get( "help.theme.list" ) )
    parser.add_argument( "-c" , "--clear" , required = False , action = "store_true" , help = lang.get( "help.clear" ) )
    parser.add_argument( "-b" , "--build" , required = False , action = "store_true" , help = lang.get( "help.build" ) )
    parser.add_argument( "-s" , "--server" , required = False , action = "store_true" , help = lang.get( "help.server" ) )
    parser.add_argument( "--port" , required = False , default = 7000 , type = int , help = lang.get( "help.server.port" ) )
    parser.add_argument( "-p" , "--push" , required = False , action = "store_true" , help = lang.get( "help.push" ) )
    parser.add_argument( "--commit" , required = False , default = None , type = str , help = lang.get( "help.push.commit" ) )
    parser.add_argument( "-n" , "--new" , required = False , action = "store_true" , help = lang.get( "help.new" ) )
    parser.add_argument( "--page" , required = False , action = "store_true" , help = lang.get( "help.page" ) )
    args = parser.parse_args()
    if args.server :
        if not os.path.exists( "output" ) :
            print( lang.get( "error.output_not_exist" ) )
            exit()
        httpd = http.server.HTTPServer( ( "0.0.0.0" , port := args.port ) , http.server.SimpleHTTPRequestHandler )
        print( f"http://0.0.0.0{ f':{ port if port != 80 else '' }' }" )
        os.chdir( "output" )
        try : httpd.serve_forever()
        except KeyboardInterrupt : ...
        exit()
    if args.init :
        # load theme
        if not os.path.isdir( path := os.path.join( home , "theme" , args.theme ) ) :
            print( lang.get( "error.theme_not_exist" ) )
            exit()
        try :
            theme = lib.theme.theme_load( path )
        except ImportError :
            print( lang.get( "error.theme_load_failed" ) )
            exit()
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
    if not os.path.exists( "output" ) : os.mkdir( "output" )

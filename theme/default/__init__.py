"""
the default theme for simplog
"""

import traceback
import typing
import shutil
import json
import time
import os

import pygments.formatters
import pygments.lexers

import mistune.plugins
import mistune

import langful
import bs4

import lib.config
import lib.theme
import lib.path
import lib.time

__all__ = [ "HTMLRenderer" , "theme" , "version" , "description" ]

class HTMLRenderer( mistune.HTMLRenderer ) :

    def block_code( self, code : str , info : str | None = None ) -> str :
        try :
            if info == "mermaid" : return f"\n<pre class=\"mermaid\">{ code }</pre>"
            elif isinstance( info , str ) :
                lexer = pygments.lexers.get_lexer_by_name( info )
                formatter = pygments.formatters.HtmlFormatter()
                return pygments.highlight( code , lexer , formatter )
        except :
            traceback.print_exc()
        return f"\n<div class=\"highlight\"><pre>{ code }</pre></div>"

    def heading( self , text : str , level : int , **_ ) -> str :
        return f"<h{ level } class=\"heading\">{ text }</h{ level }>"

class theme( lib.theme.theme ) :

    def init( self ) -> None :
        self.set_config_theme()

    def main( self ) -> None :
        self.lang = langful.langful( os.path.join( os.path.dirname( __file__ ) , "lang" ) )
        self.config = self.set_config_theme()
        self.markdown = mistune.Markdown( HTMLRenderer( False ) , plugins = [ mistune.plugins.import_plugin( plugin ) for plugin in self.config.get( "mistune_plugins" ) ] )

    def set_config_theme( self ) -> lib.config.parser :
        with lib.config.parser( os.path.join( self.path_source , "config" , "theme.json" ) , check_exist = False ) as config :
            config.add( "giscus" , {
                "src" : "https://giscus.app/client.js"
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

    def set_config_info( self , path : str , check_exist : bool = False ) -> lib.config.parser :
        with lib.config.parser( os.path.join( path , "info.json" ) , check_exist ) as config :
            config.add( "title" , None )
            config.add( "description" , None )
            config.add( "comment" , True )
        return config

    def set_config_page( self , path : str , check_exist : bool = False ) -> lib.config.parser :
        with lib.config.parser( os.path.join( path , "page.json" ) , check_exist ) as config :
            config.add( "template" , "post" )
            config.add( "from" , None )
            config.add( "to" , None )
        return config

    def to_html( self , text : str ) -> str :
        return str( self.markdown( text ) )

    def load_info_post( self , path : str ) -> tuple[ dict[ str , typing.Any ] , str , str , str ] :
        info = self.set_config_info( path , True ).data
        if os.path.exists( os.path.join( path , "page.json" ) ) : page = self.set_config_page( path , True ).data
        else : page = { "from" : "index.md" , "to" : os.path.join( "post" , info[ "id" ] , "index.html" ) , "template" : "post" }
        return info , os.path.join( path , page[ "from" ] ) , page[ "to" ] , page[ "template" ]

    def load_info_page( self , path : str , post : bool = False ) -> tuple[ dict[ str , typing.Any ] , str , str , str ] :
        page = self.set_config_page( path , True ).data
        return self.set_config_info( path , True ).data , os.path.join( path , page[ "from" ] ) , page[ "to" ] , page[ "template" ]

    def build( self , output : str ) -> None :
        print( self.lang.get( "build.info.start" ) )
        giscus_args = self.config.get( "giscus" )
        if isinstance( giscus_args , dict ) : giscus_args[ "async" ] = None
        else : giscus_args = None
        giscus : bs4.element.Tag | None = None if giscus_args is None else bs4.BeautifulSoup().new_tag( "script" , **giscus_args )
        pages : list[ tuple[ str , bool ] ] = [ ( os.path.join( self.path_source , "page" , path ) , False ) for path in os.listdir( os.path.join( self.path_source , "page" ) ) ]
        len_page = len( pages )
        failed_page = failed_post = 0
        [ lib.path.checkdir( os.path.join( self.path_source , path ) ) for path in ( "post" , "page" ) ]
        [ [ [ pages.append( ( os.path.join( self.path_source , "post" , year , path , name ) , True ) ) for name in os.listdir( os.path.join( self.path_source , "post" , year , path ) ) ] for path in os.listdir( os.path.join( self.path_source , "post" , year ) ) ] for year in os.listdir( os.path.join( self.path_source , "post" ) ) ]
        if len( pages ) : print( self.lang.replace( "build.info.pages" , { "all" : len( pages ) , "page" : len_page , "post" : len( pages ) - len_page } ) )
        post_info : list[ dict[ str , typing.Any ] ] = []
        templates : dict[ str , str ] = {}
        for path , is_post in pages :
            try :
                # get template
                info , file , to , template_name = ( self.load_info_page , self.load_info_post )[ is_post ]( path )
                if template_name not in templates :
                    with open( os.path.join( self.path_source , "template" , template_name + ".html" ) , "r" , encoding = "utf-8" ) as fp :
                        data = fp.read()
                    templates[ template_name ] = data
                else : data = templates[ template_name ]
                template = bs4.BeautifulSoup( data , "html.parser" )
                # set info
                if is_post : post_info.append( info )
                # find element
                div_post = template.find( "div" , id = "post" )
                div_title = template.find( "div" , id = "title" )
                div_commit = template.find( "div" , id = "commit" )
                head = template.find( "head" )
                # set title
                if isinstance( head , bs4.element.Tag ) :
                    title = bs4.BeautifulSoup().new_tag( "title" )
                    title.string = info[ "title" ]
                    head.append( title )
                if isinstance( div_title , bs4.element.Tag ) :
                    title = bs4.BeautifulSoup().new_tag( "h1" )
                    title.string = info[ "title" ]
                    div_title.append( title )
                    if ( description := info[ "description" ] ) :
                        p = bs4.BeautifulSoup().new_tag( "p" , id = "description" )
                        p.string = description
                        div_title.append( p )
                if isinstance( div_post , bs4.element.Tag ) :
                    with open( file , "r" , encoding = "utf-8" ) as fp : div_post.append( bs4.BeautifulSoup( self.to_html( fp.read() ) , "html.parser" ) )
                # giscus
                if isinstance( div_commit , bs4.element.Tag ) :
                    if giscus is not None : div_commit.append( giscus )
                    else : div_commit.decompose()
                # write file
                lib.path.checkdir( os.path.dirname( to := os.path.join( output , to ) ) )
                with open( to , "wb" ) as fp : fp.write( template.prettify( "utf-8" ) )
                # copy files
                if is_post and isinstance( info[ "files" ] , list ) :
                    for file in info[ "files" ] :
                        if not os.path.exists( file := os.path.join( path , file ) ) : continue
                        dst = os.path.join( output , "post" , info[ "id" ] , os.path.split( file )[ -1 ] )
                        if os.path.isfile( file ) : shutil.copyfile( file , dst )
                        else : lib.path.copytree( file , dst )
            except :
                traceback.print_exc()
                print( self.lang.get( "build.error.failed.conversion" ) )
                if is_post : failed_post += 1
                else : failed_page += 1
                continue
        lib.path.checkdir( os.path.dirname( path := os.path.join( output , "api" , "post.json" ) ) )
        post_info.sort( key = lambda data : data[ "time" ] , reverse = True )
        with open( path , "w" ) as fp : json.dump( post_info , fp )
        if failed_page + failed_post : print( self.lang.replace( "build.info.failed" , { "page" : failed_page , "post" : failed_post } ) )
        else : print( self.lang.get( "build.info.no_failed" ) )
        print( self.lang.get( "build.info.done" ) )

    def post( self , path : str , title : str ) -> None :
        seconds = time.time()
        lib.path.checkfile( os.path.join( path , "index.md" ) )
        with self.set_config_info( path ) as info :
            info.set( "id" , lib.time.to_hex( seconds ) )
            info.set( "time" , int( seconds ) )
            info.set( "title" , title )
            info.set( "tags" , [] )
            info.add( "files" , [] )

    def page( self , path : str , title : str ) -> None :
        name = title + ".md"
        lib.path.checkfile( os.path.join( path , name ) )
        with self.set_config_info( path ) as info :
            info.set( "title" , title )
        with self.set_config_page( path ) as page :
            page.set( "from" , name )
            page.set( "to" , os.path.join( "page" , info.get( "id" ) + ".html" ) )

name = "Azure"
theme_class = theme
version = __version__ = "0.0.2"
description = "the default theme for simplog"
requirement = os.path.join( os.path.dirname( __file__ ) , "requirements.txt" )

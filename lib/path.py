import shutil
import re
import os

__all__ = [ "checkdir" , "checkfile" , "copytree" , "formatname" ]

def checkdir( path : str ) -> None :
    if not os.path.exists( path ) : os.makedirs( path )

def checkfile( path : str ) -> None :
    if os.path.exists( path ) :
        if os.path.isdir( path ) : shutil.rmtree( path )
        else : return
    checkdir( os.path.split( path )[ 0 ] )
    with open( path , "wb" ) : pass

def copytree( src : str , dst : str ) -> None :
    for root , dirs , files in os.walk( src ) :
        to = os.path.relpath( root , os.path.commonpath( ( src , root ) ) )
        [ checkdir( os.path.join( dst , p ) ) for p in dirs ]
        path = os.path.join( dst , to )
        checkdir( path )
        [ shutil.copyfile( os.path.join( root , file ) , os.path.join( path , file ) ) for file in files ]

def rmtree( dst : str , blacklist : list[ str ] | None = None ) -> None :
    dst = os.path.relpath( dst )
    blacklists = set()
    if blacklist is None : blacklist = []
    for item in ( os.path.relpath( os.path.join( dst , path ) ) for path in blacklist ) :
        blacklists.add( item )
        while True :
            item = os.path.dirname( item )
            if not item : break
            blacklists.add( item )
    [ [ ( os.rmdir , os.remove )[ os.path.isfile( path ) ]( path ) for path in [ os.path.join( root , path ) for path in dirs + files ] if path not in blacklists ] for root , dirs , files in os.walk( dst , False ) ]

def formatname( name : str ) -> str :
    name = name.strip()
    if name and name[ 0 ] == "." : name = name[ 1 : ]
    if name and name[ -1 ] == "." : name = name[ : -1 ]
    name = name.replace( " " , "-" )
    name = re.sub( """[<>:"/\\|?*]""" , "_" ,  name )
    return name[ : 255 ]

import typing
import json
import os

__all__ = [ "parser" ]

class parser :

    def __enter__( self ) -> "parser" :
        return self

    def __exit__( self , *_ ) -> None :
        self.dump()

    def __init__( self , path : str , check_exist : bool = True ) -> None :
        if os.path.isfile( path ) :
            with open( path , "r" , encoding = "utf-8" ) as fp : data = json.load( fp )
        elif not check_exist :
            data = {}
        else :
            raise FileNotFoundError( "cannot find the config file" )
        self.data : dict[ str , typing.Any ] = data
        self.path : str = path

    def add( self , key : str , default : typing.Any ) -> None :
        if key not in self.data : self.data[ key ] = default

    def dump( self ) -> None :
        with open( self.path , "w" , encoding = "utf-8" ) as fp : json.dump( self.data , fp , ensure_ascii = False , indent = 4 )

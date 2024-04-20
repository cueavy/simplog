import importlib.util
import types
import abc
import os

__all__ = [ "theme_load" ]

def theme_load( path : str , name : str | None = None ) -> types.ModuleType :
    if name is None : name = os.path.split( path )[ -1 ]
    spec = importlib.util.spec_from_file_location( name , os.path.join( path , "__init__.py" ) )
    if spec is None or spec.loader is None : raise ImportError
    module = importlib.util.module_from_spec( spec )
    spec.loader.exec_module( module )
    if not hasattr( module , "theme" ) or not isinstance( module.theme() , theme ) : raise ImportError
    return module

class theme :

    def __init__( self , path : str | None = None ) -> None :
        """
        theme class init
        """
        self.path : str = os.getcwd() if path is None else path

    @abc.abstractmethod
    def init( self ) -> None :
        """
        blog frame init
        """
        pass

    @abc.abstractmethod
    def main( self ) -> None :
        pass

    @abc.abstractmethod
    def build( self ) -> None :
        pass

    @abc.abstractmethod
    def post( self , path : str , title : str ) -> None :
        pass

    @abc.abstractmethod
    def page( self , path : str , title : str ) -> None :
        pass

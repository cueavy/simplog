import importlib.util
import types
import os

__all__ = [ "theme_load" ]

def theme_load( path : str , name : str | None = None ) -> types.ModuleType :
    if name is None : name = os.path.split( path )[ -1 ]
    spec = importlib.util.spec_from_file_location( name , os.path.join( path , "__init__.py" ) )
    if spec is None or spec.loader is None : raise ImportError
    module = importlib.util.module_from_spec( spec )
    spec.loader.exec_module( module )
    return module

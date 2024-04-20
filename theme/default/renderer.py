import pygments.formatters
import pygments.lexers
import traceback
import pygments
import mistune

__all__ = [ "HTMLRenderer" ]

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

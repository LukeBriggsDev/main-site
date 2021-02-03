import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang=None):
        if lang:
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
                formatter = html.HtmlFormatter(style='monokai', noclasses=True)
                return highlight(code, lexer, formatter)
            except ValueError:
                pass
        return '<pre><code>' + mistune.escape(code) + '</code></pre>'



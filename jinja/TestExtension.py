from jinja2 import nodes
from jinja2.ext import Extension


class ScriptExtension(Extension):
    tags = set(['script'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        ctx_ref = nodes.ContextReference()

        body = parser.parse_statements(['name:endscript'], drop_needle=True)

        # TODO: Check we've an output node
        # if this is not 'unsafe' and we have dangerous children, bail out
        if len(body[0].nodes) > 1 or type(body[0].nodes[0]) != nodes.TemplateData:
            raise Exception('{% script %} tag has an unsafe body')

        node = self.call_method('_render_script', [ctx_ref], lineno=lineno)
        return nodes.CallBlock(node, [], [], body).set_lineno(lineno)

    def _render_script(self, context, caller):
        """Helper callback."""
        nonce = context['csp_nonce']
        rv = "<script nonce=\"%s\">" % (nonce) + caller() + "</script>"
        return rv

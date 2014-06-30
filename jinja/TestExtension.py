from jinja2 import nodes
from jinja2.ext import Extension


class ScriptExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['script'])

    def __init__(self, environment):
        super(ScriptExtension, self).__init__(environment)

        # add the defaults to the environment
        environment.extend(
        )

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]
        print args

        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        # now we parse the body of the script block up to `endscript` and
        # drop the needle (which would always be `endscript` in that case)
        body = parser.parse_statements(['name:endscript'], drop_needle=True)
        if len(body[0].nodes) > 1:
            raise Exception('Oh noes!')

        # now return a `CallBlock` node that calls our _script_support
        # helper method on this extension.
        return nodes.CallBlock(self.call_method('_script_support', args),
                               [], [], body).set_lineno(lineno)

    def _script_support(self, name, timeout, caller):
        """Helper callback."""
        print 'in support',name
        rv = caller()
        return rv

from jinja2 import Environment

env = Environment(extensions=[ScriptExtension])

from jinja2 import Template
t = """{% script 'something' %}
<div class="sidebar">
</div>
{% endscript %}"""
template = env.from_string(t)
print template.render()

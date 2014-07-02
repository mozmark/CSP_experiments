from jinja2 import Environment
from TestExtension import ScriptExtension

env = Environment(extensions=[ScriptExtension])

from jinja2 import Template
t = """{% script %}
{% endscript %}"""
template = env.from_string(t)
print template.render({'example':123,'csp_nonce':'wibble'})

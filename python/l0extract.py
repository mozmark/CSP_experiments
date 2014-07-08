import html5lib
import random
import string
import sys
from lxml import etree

def createID(n=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def extractHandlers(html):
    script_lines = []
    handlers = {}
    document = html5lib.parse(html, namespaceHTMLElements=False, treebuilder="lxml")
    for em in document.iter():
        node_handlers = {}
        emID = None
        # copy on* handlers out
        for att in em.attrib.keys():
            if 0 == att.find('on'):
                node_handlers[att] = em.attrib[att]
        # remove them from the node
        for att in node_handlers.keys():
            em.attrib.pop(att)
        # ensure the element has an ID
        if 0 < len(node_handlers):
            if not 'id' in em.attrib.keys():
                # TODO: it'd be nice if IDs could be nice and sensible for e.g. body
                emID = createID()
                em.attrib['id'] = emID
            else:
                emID = em.attrib['id']
        handlers[emID] = node_handlers
    for emID in handlers.keys():
        handlers_for_ID = handlers[emID]
        for handler in handlers_for_ID.keys():
            line = handlers_for_ID[handler]
            body = line
            if not line.rstrip().endswith(';'):
                body = line + ';'
            handler_script = """
document.getElementById('%s').addEventListener('%s',
    function(evt) {
        if(!function(evt) {
            %s
            return true;
        }(evt)){
            evt.preventDefault();
        }
    }, false);
"""%(emID, handler[2:], body)
            script_lines.append(handler_script)

    script = """
window.addEventListener("load",function() {
%s
}, false);
"""%('\n'.join(script_lines))
    emSC = etree.SubElement(document.xpath('/html/head')[0],'script')
    emSC.text = script

    print etree.tostring(document, pretty_print=True)

if __name__ == '__main__':
    html_files = sys.argv[1:]
    for html_file in html_files:
        f = open(html_file, 'r')
        html = f.read()
        extractHandlers(html)
        f.close()

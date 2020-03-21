import xml.etree.ElementTree as ET

def head(elem):
    : <!DOCTYPE html>
    : <html>
    : <head>
    : <meta charset="UTF-8">
    : <link rel="stylesheet" type="text/css" href="${stylesheet}">
    : </head>
    : <body>
    : <div class="page-container">

def group(pass_, elem):
    : <h2 class="${elem.tag}-groupinfo-name">${elem.findtext("name")}</h2>
    if elem.find("abstract") is not None:
        : <div class="${elem.tag}-groupinfo-abstract">${pretty_text(elem.find("abstract"))}</div>
    if elem.find("desc") is not None:
        : <div class="${elem.tag}-groupinfo-desc">${pretty_text(elem.find("desc"))}</div>
def section(pass_, elem, title):
    : <h3 class="section">${title}</h3>

def item_head(pass_, elem):
    collapsible = elem.tag in [
        "class", "category", "protocol", "com_interface",
        "method", "property", "function", "variable",
        "constant", "struct", "union", "enum",
        "typedef", "pdefine"]
    desi = ""
    if "category" == elem.tag:
        desi = "Category "
    elif "protocol" == elem.tag:
        desi = "Protocol "
    elif "method" == elem.tag and "occ" == elem.get("lang"):
        if "instm" == elem.get("type"):
            desi = "- "
        elif "clm" == elem.get("type"):
            desi = "+ "
    name = pretty_text(elem.find("name"))
    abst = pretty_text(elem.find("abstract"))
    : <a id="${elem.get("id")}" name="${elem.get("id")}"></a>
    : <a id="${name}" name="${name}"></a>
    if collapsible:
        : <details>
        : <summary>
        : <div class="summary">
        : <h1 class="${elem.tag}-name">${desi}${name}</h1>
        if abst:
            : <div class="${elem.tag}-abstract">${abst}</div>
        : </div>
        : </summary>
        : <div class="collapsible">
        : <div class="pointy-thing"></div>
    else:
        : <div class="summary">
        : <h1 class="${elem.tag}-name">${desi}${name}</h1>
        if abst:
            : <div class="${elem.tag}-abstract">${abst}</div>
        : </div>
def item(pass_, elem):
    if elem.tag in [
        "method", "property", "function", "variable",
        "constant", "struct", "union", "enum",
        "typedef", "pdefine"]:
        if elem.find("declaration") is not None:
            : <pre class="${elem.tag}-declaration">
            : ${pretty_text(elem.find("declaration"))}
            : </pre>
    if elem.find("fieldlist") is not None:
        : <h2 class="${elem.tag}-fieldlist">Fields</h2>
        : <table class="${elem.tag}-fieldlist">
        : <tbody>
        for e in elem.findall("fieldlist/field"):
            : <tr class="${elem.tag}-${e.tag}">
            : <td class="${elem.tag}-${e.tag}-name"><p>${pretty_text(e.find("name"))}</p></td>
            : <td class="${elem.tag}-${e.tag}-desc">${pretty_text(e.find("desc"))}</td>
            : </tr>
        : </tbody>
        : </table>
    if elem.find("parameterlist") is not None:
        : <h2 class="${elem.tag}-parameterlist">Parameters</h2>
        : <table class="${elem.tag}-parameterlist">
        : <tbody>
        for e in elem.findall("parameterlist/parameter"):
            : <tr class="${elem.tag}-${e.tag}">
            : <td class="${elem.tag}-${e.tag}-name"><p>${pretty_text(e.find("name"))}</p></td>
            : <td class="${elem.tag}-${e.tag}-desc">${pretty_text(e.find("desc"))}</td>
            : </tr>
        : </tbody>
        : </table>
    if elem.find("result") is not None:
        : <h2 class="${elem.tag}-result">Return Value</h2>
        : <div class="${elem.tag}-result">${pretty_text(elem.find("result"))}</div>
    if elem.find("throwlist") is not None:
        : <h2 class="${elem.tag}-throwlist">Throws</h2>
        for e in elem.findall("throwlist/throw"):
            : <div class="${elem.tag}-throw">${pretty_text(e)}</div>
    if elem.find("desc") is not None:
        if not elem.tag in ["header", "framework"]:
            : <h2 class="${elem.tag}-desc">Discussion</h2>
        : <div class="${elem.tag}-desc">${pretty_text(elem.find("desc"))}</div>
    if elem.find("attributelists") is not None:
        for e in elem.findall("attributelists/listattribute"):
            if "See" == e.findtext("name"):
                : <h2 class="${elem.tag}-see">See Also</h2>
                : <div class="${elem.tag}-see">
                for f in e.findall(".//hd_link"):
                    : <a class="${elem.tag}-see" href="#${f.get("logicalPath")}">${pretty_text(f)}</a>
                    : <br>
                : </div>
def item_foot(pass_, elem):
    collapsible = elem.tag in [
        "class", "category", "protocol", "com_interface",
        "method", "property", "function", "variable",
        "constant", "struct", "union", "enum",
        "typedef", "pdefine"]
    if collapsible:
        : </div>
        : </details>

def foot(elem):
    copyright = pretty_text(elem.find("copyrightinfo"))
    timestamp = pretty_text(elem.find("timestamp"))
    if copyright or timestamp:
        : <div class="copyright">
        if copyright:
            : Copyright ${copyright}
        if copyright and timestamp:
            : &nbsp;|&nbsp;
        if timestamp:
            : Updated: ${timestamp}
        : </div>
    : </div>
    : </body>
    : </html>

pretty_text_map = {
    "hd_link": lambda e: ("a", { "href": pretty_link(e) }),
    "declaration_comment": ("span", { "class": "dcmt" }),
    "declaration_string": ("span", { "class": "dstr" }),
    "declaration_char": ("span", { "class": "dchr" }),
    "declaration_preprocessor": ("span", { "class": "dpre" }),
    "declaration_number": ("span", { "class": "dnum" }),
    "declaration_keyword": ("span", { "class": "dkwd" }),
    "declaration_function": ("span", { "class": "dfun" }),
    "declaration_var": ("span", { "class": "dvar" }),
    "declaration_template": ("span", { "class": "dtpl" }),
    "declaration_type": ("span", { "class": "dtyp" }),
    "declaration_param": ("span", { "class": "dpar" }),
    "declaration_availabilitymacro": ("span", { "class": "davm" }),
}
def pretty_link(elem):
    link = elem.get("logicalPath", "")
    if link.startswith("//href/doc/"):
        link = link.replace("//href/doc/", "")
        return link
    link = link.replace("//apple_ref/doc/", "")
    if link:
        link += file_extension()
    return link
def pretty_text_append(l, elem):
    if hasattr(elem, "text"):
        pretty_text_append(l, elem.text or "")
        for e in elem:
            tup = pretty_text_map.get(e.tag, (e.tag, e.attrib))
            if callable(tup):
                tup = tup(e)
            tag, atr = tup
            l.append("<%s" % tag)
            for k, v in sorted(atr.items()):
                l.append(' %s="%s"' % (k, v.\
                    replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;").\
                    replace("\"", "&quot;").replace("\n", "&#10;")))
            if e.text or len(e):
                l.append(">")
                pretty_text_append(l, e)
                l.append("</%s>" % tag)
            else:
                l.append(" />")
            pretty_text_append(l, e.tail or "")
    else:
        l.append((elem or "").replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;"))
def pretty_text(elem):
    l = []
    pretty_text_append(l, elem)
    return "".join(l)

def file_extension():
    return ".html"
def passes(elem):
    return ["main"]

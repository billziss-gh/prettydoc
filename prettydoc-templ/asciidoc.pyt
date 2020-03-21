# -*- coding: UTF-8 -*-

def head(elem):
    pass

def group(pass_, elem):
    : == ${elem.findtext("name")}
    :
    if elem.find("abstract") is not None:
        : ${pretty_text(elem.find("abstract"))}
        :
    if elem.find("desc") is not None:
        : ${pretty_text(elem.find("desc"))}
        :
def section(pass_, elem, title):
    if elem.tag not in ["class", "category", "protocol", "com_interface"]:
        : === ${title}
    else:
        : ==== ${title}
    :

def item_head(pass_, elem):
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
    if elem.tag in ["framework", "header"]:
        global lang
        lang = elem.get("lang")
        copyright = pretty_text(elem.find("copyrightinfo"))
        : = ${name}
        if copyright:
            : :author: ${copyright}
        : :toc: preamble
        : :toc-title:
        :
        if abst:
            : ${abst}
            :
    else:
        if abst:
            : *${desi}${name}* - ${abst}
            :
        else:
            : *${desi}${name}*
            :
def item(pass_, elem):
    if elem.tag in [
        "method", "property", "function", "variable",
        "constant", "struct", "union", "enum",
        "typedef", "pdefine"]:
        if elem.find("declaration") is not None:
            : ${pretty_declaration(elem.find("declaration"))}
            :
    if elem.find("fieldlist") is not None:
        : *Fields*
        :
        for e in elem.findall("fieldlist/field"):
            : - _${pretty_text(e.find("name"))}_ - ${pretty_text(e.find("desc"))}
        :
    if elem.find("parameterlist") is not None:
        : *Parameters*
        :
        for e in elem.findall("parameterlist/parameter"):
            : - _${pretty_text(e.find("name"))}_ - ${pretty_text(e.find("desc"))}
        :
    if elem.find("result") is not None:
        : *Return Value*
        :
        : ${pretty_text(elem.find("result"))}
        :
    if elem.find("throwlist") is not None:
        : *Throws*
        :
        for e in elem.findall("throwlist/throw"):
            : - ${pretty_text(e)}
        :
    if elem.find("desc") is not None:
        if not elem.tag in ["header", "framework"]:
            : *Discussion*
            :
        : ${pretty_text(elem.find("desc"))}
        :
    if elem.find("attributelists") is not None:
        for e in elem.findall("attributelists/listattribute"):
            if "See" == e.findtext("name"):
                : *See Also*
                :
                for f in e.findall(".//hd_link"):
                    : - ${pretty_text(f)}
                :
def item_foot(pass_, elem):
    :

def foot(elem):
    pass

pretty_text_map = {
    "hd_link": lambda e: "link:%s[%s]%s" % (pretty_link(e), e.text, e.tail or ""),
    "img": lambda e: "image:%s[%s]" % (e.get("src", ""), e.get("alt", "")),
    "i": ("_", "_"),
    "b": ("*", "*"),
    "code": ("`", "`"),
    "p": ("", "\n\n"),
    "ul": ("", "\n"),
    "li": ("- ", "\n"),
}
def pretty_link(elem):
    link = elem.get("logicalPath", "")
    if link.startswith("//href/doc/"):
        link = link.replace("//href/doc/", "")
        return link
    link = link.replace("//apple_ref/doc/", "")
    return link
def pretty_text_append(l, elem):
    if hasattr(elem, "text"):
        pretty_text_append(l, elem.text or "")
        for e in elem:
            tup = pretty_text_map.get(e.tag, ("", ""))
            if callable(tup):
                tup = tup(e)
                l.append(tup)
            else:
                sta, end = tup
                l.append(sta)
                pretty_text_append(l, e)
                l.append(end)
                pretty_text_append(l, e.tail or "")
    else:
        l.append((elem or "").strip("\r\n").\
            replace("\\", "$$\\$$").replace("_", "$$_$$").replace("*", "$$*$$").\
            replace("::", "$$::$$").\
            replace(u"©", "(C)"))
def pretty_text(elem):
    l = []
    pretty_text_append(l, elem)
    return "".join(l).strip()
def pretty_declaration(elem):
    if elem is None:
        return None
    text = "".join([(e.text or "") + (e.tail or "") for e in elem])
    if text:
        text = "----\n" + text + "\n----"
        if lang:
            text = "[source,%s]\n" % lang + text
    return text

def file_extension():
    return ".asciidoc"
def passes(elem):
    return ["main"]

# -*- coding: UTF-8 -*-

def head(elem):
    pass

def group(pass_, elem):
    : .SS ${elem.findtext("name").upper()}
    if elem.find("abstract") is not None:
        : ${pretty_text(elem.find("abstract"))}
    if elem.find("desc") is not None:
        : ${pretty_text(elem.find("desc"))}
    else:
        : \&
        : .br
def section(pass_, elem, title):
    : \fB${title.upper()}\fP
    :

def item_head(pass_, elem):
    name = pretty_text(elem.find("name"))
    abst = pretty_text(elem.find("abstract"))
    if elem.tag in ["header", "framework"]:
        if "toc" == pass_:
            : .TH "${name}" 3 "${pretty_text(elem.find("timestamp"))}"
            : .SH NAME
            : \&
            : .br
            if abst:
                : ${name} \- ${abst}
            else:
                : ${name}
            :
            : .SH SYNOPSIS
            : \&
            : .br
        else:
            : .SH DESCRIPTION
            : \&
            : .br
    else:
        if abst:
            : \fB${name}\fP \- ${abst}
        else:
            : \fB${name}\fP
        if "toc" != pass_:
            : .RS 4
            :
def item(pass_, elem):
    if "toc" == pass_:
        return
    if elem.tag in [
        "method", "property", "function", "variable",
        "constant", "struct", "union", "enum",
        "typedef", "pdefine"]:
        if elem.find("declaration") is not None:
            : ${pretty_declaration(elem.find("declaration"))}
            :
    if elem.find("fieldlist") is not None:
        : \fBFields\fP
        : .RS 4
        for i, e in enumerate(elem.findall("fieldlist/field")):
            if 0 < i:
                :
            : \fI${pretty_text(e.find("name"))}\fP \- ${pretty_text(e.find("desc"))}
        : .RE
        :
    if elem.find("parameterlist") is not None:
        : \fBParameters\fP
        : .RS 4
        for i, e in enumerate(elem.findall("parameterlist/parameter")):
            if 0 < i:
                :
            : \fI${pretty_text(e.find("name"))}\fP \- ${pretty_text(e.find("desc"))}
        : .RE
        :
    if elem.find("result") is not None:
        : \fBReturn Value\fP
        : .RS 4
        : ${pretty_text(elem.find("result"))}
        : .RE
        :
    if elem.find("throwlist") is not None:
        : \fBThrows\fP
        : .RS 4
        for i, e in enumerate(elem.findall("throwlist/throw")):
            if 0 < i:
                :
            : ${pretty_text(e)}
        : .RE
        :
    if elem.find("desc") is not None:
        if not elem.tag in ["header", "framework"]:
            : \fBDiscussion\fP
            : .RS 4
            : ${pretty_text(elem.find("desc"))}
            : .RE
            :
        else:
            : ${pretty_text(elem.find("desc"))}
            :
    if elem.find("attributelists") is not None:
        for e in elem.findall("attributelists/listattribute"):
            if "See" == e.findtext("name"):
                : \fBSee Also\fP
                : .RS 4
                for f in e.findall(".//hd_link"):
                    : ${pretty_text(f)}
                    : .br
                : .RE
                :
def item_foot(pass_, elem):
    if not elem.tag in ["header", "framework"]:
        if "toc" != pass_:
            : .RE
    :

def foot(elem):
    copyright = pretty_text(elem.find("copyrightinfo"))
    if copyright:
        : .SH COPYRIGHT
        : \&
        : .br
        : ${copyright}

pretty_text_map = {
    "i": (r"\fI", r"\fP"),
    "b": (r"\fB", r"\fP"),
    "code": (r"\f[CW]", r"\fP"),
    "p": ("", "\n\n"),
    "li": (".IP \(bu 4\n", "\n.PP\n"),
}
def pretty_escape(text):
    return text.replace("\\", "\\\\").replace(u"©", "\[co]")
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
        l.append(pretty_escape((elem or "").strip("\r\n")))
def pretty_text(elem):
    l = []
    pretty_text_append(l, elem)
    return "".join(l).strip()
def pretty_declaration(elem):
    if elem is None:
        return None
    fontmap = {
        "declaration_preprocessor": r"\fB%s\fP",
        "declaration_keyword": r"\fB%s\fP",
        "declaration_function": r"\fB%s\fP",
        "declaration_var": r"\fI%s\fP",
        "declaration_template": r"\fB%s\fP",
        "declaration_type": r"\fB%s\fP",
        "declaration_param": r"\fI%s\fP",
        "declaration_availabilitymacro": r"\fB%s\fP",
    }
    return "".join([fontmap.get(e.tag, "%s") % pretty_escape(e.text or "") + \
        pretty_escape(e.tail or "") for e in elem])

def file_extension():
    return ".3"
def passes(elem):
    return ["toc", "main"]

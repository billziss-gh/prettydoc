#!/usr/bin/env python
#
# Copyright (c) 2014-2016, Bill Zissimopoulos. All rights reserved.
#
# Redistribution  and use  in source  and  binary forms,  with or  without
# modification, are  permitted provided that the  following conditions are
# met:
#
# 1.  Redistributions  of source  code  must  retain the  above  copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions  in binary  form must  reproduce the  above copyright
# notice,  this list  of conditions  and the  following disclaimer  in the
# documentation and/or other materials provided with the distribution.
#
# 3.  Neither the  name  of the  copyright  holder nor  the  names of  its
# contributors may  be used  to endorse or  promote products  derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY  THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND  ANY EXPRESS OR  IMPLIED WARRANTIES, INCLUDING, BUT  NOT LIMITED
# TO,  THE  IMPLIED  WARRANTIES  OF  MERCHANTABILITY  AND  FITNESS  FOR  A
# PARTICULAR  PURPOSE ARE  DISCLAIMED.  IN NO  EVENT  SHALL THE  COPYRIGHT
# HOLDER OR CONTRIBUTORS  BE LIABLE FOR ANY  DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL,  EXEMPLARY,  OR  CONSEQUENTIAL   DAMAGES  (INCLUDING,  BUT  NOT
# LIMITED TO,  PROCUREMENT OF SUBSTITUTE  GOODS OR SERVICES; LOSS  OF USE,
# DATA, OR  PROFITS; OR BUSINESS  INTERRUPTION) HOWEVER CAUSED AND  ON ANY
# THEORY  OF LIABILITY,  WHETHER IN  CONTRACT, STRICT  LIABILITY, OR  TORT
# (INCLUDING NEGLIGENCE  OR OTHERWISE) ARISING IN  ANY WAY OUT OF  THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# pytempl.py(1)
# =============
#
# NAME
# ----
# pytempl.py - Python Template Language
#
# SYNOPSIS
# --------
# pytempl.py file [args...]
#
# DESCRIPTION
# -----------
# The *pytempl.py* module implements the Python Template Language. It is
# intended to be used by Python code using *import pytempl*. It can also
# be executed as a script directly from the command line, in which case
# it treats its first argument as a Python Template Language file to be
# executed and passes the rest of the arguments to it.
#
# PYTHON TEMPLATE LANGUAGE
# ------------------------
# *Pytempl* templates are essentially Python source code with the addition
# of a single new feature, the *:* construct.
#
# The *:* construct is a shortcut for embedding text to be output in Python
# source. Everything placed after a *:* will be copied to the output, Python
# expressions can also be inserted by using the *${ python expression }*
# construct (similar to shell expansion).
#
# Example:
#
#     : <summary>
#     : <div class="summary">
#     : <h1 class="${elem.tag}-name">${name}</h1>
#     if abst:
#         : <div class="${elem.tag}-abstract">${abst}</div>
#     : </div>
#     : </summary>
#
# COPYRIGHT
# ---------
# (C) 2014-2016 Bill Zissimopoulos

import imp, os, re, sys

# begin template engine
template_copy_re = re.compile(r"^(\s*): ?(.*)", re.DOTALL)
template_expr_re = re.compile(r"\$\{([^}]+)\}")
template_copy_stmt = ("_.write(%r.encode('UTF-8'))", "_.write(unicode(%s).encode('UTF-8'))")
def template_translate(source):
    for line in source:
        m = template_copy_re.search(line)
        if m:
            line = m.group(1) + ";".join(template_copy_stmt[i % 2] % p
                for i, p in enumerate(template_expr_re.split(m.group(2))) if p) + "\n"
        yield line
def template_compile(source, fullpath, dict):
    exec(compile("".join(template_translate(source)), fullpath, "exec"), dict)
def template_load(fullpath, _=None):
    n = os.path.splitext(os.path.basename(fullpath))[0]
    m = imp.new_module(n)
    m.__file__ = fullpath
    m.__loader__ = None
    m.__package__ = ""
    if _ is not None:
        m._ = _
    with open(fullpath) as source:
        template_compile(source, fullpath, m.__dict__)
    return m
# end template engine -- seriously!

# pytempl import hook; allows importing .pyt files directly
class finder(object):
    def find_module(self, fullname, pathlist=None):
        if pathlist is None:
            filepath = os.path.join(*fullname.split(".")) + ".pyt"
            pathlist = sys.path
        else:
            filepath = os.path.join(*fullname.split(".")[1:]) + ".pyt"
        for fullpath in pathlist:
            fullpath = os.path.join(fullpath, filepath)
            if os.path.isfile(fullpath):
                return loader(fullpath)
        return None
    def __pytempl__(self):
        pass
class loader(object):
    def __init__(self, fullpath):
        self.fullpath = fullpath
    def load_module(self, fullname):
        m = oldm = sys.modules.get(fullname)
        if m is None:
            m = sys.modules[fullname] = imp.new_module(fullname)
        m.__file__ = self.fullpath
        m.__loader__ = self
        m.__package__ = fullname.rpartition('.')[0]
        try:
            with open(self.fullpath) as source:
                template_compile(source, self.fullpath, m.__dict__)
            return m
        except:
            if oldm is None:
                del sys.modules[fullname]
            raise
sys.meta_path = filter(lambda f: not hasattr(f, "__pytempl__"), sys.meta_path)
sys.meta_path.append(finder())

def warn(s):
    print >> sys.stderr, "%s: %s" % (os.path.basename(sys.argv[0]), s)
def fail(s, exitcode = 1):
    warn(s)
    sys.exit(exitcode)
def main():
    if 1 < len(sys.argv):
        del sys.argv[0]
        template_load(sys.argv[0], sys.stdout)
def __entry():
    try:
        main()
    except EnvironmentError, ex:
        fail(ex)
    except KeyboardInterrupt:
        fail("interrupted", 130)
if "__main__" == __name__:
    __entry()

import string

alphanumeric = string.letters + string.digits

def BeanshellEscapeString(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


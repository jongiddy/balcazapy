import string

alphanumeric = string.letters + string.digits

def BeanshellEscapeString(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

def getAbsolutePathRelativeToCaller(path):
    import inspect, os
    # the caller of the caller of this function is 3rd in the stack
    callerFrame = inspect.stack()[2]
    # the pathname is 2nd element n the returned tuple
    callerPath = callerFrame[1]
    # Get the absolute directory containing the caller's file
    directory = os.path.dirname(os.path.abspath(callerPath))
    # Create an absolute path for the given file
    return os.path.join(directory, path)
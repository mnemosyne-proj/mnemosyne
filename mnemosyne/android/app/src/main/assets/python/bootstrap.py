"""
 This file is executed when the Python interpreter is started.
 Use this file to configure all your necessary python code.

"""

import json


def router(args):
    """
    Defines the router function that routes by function name.

    :param args: JSON arguments
    :return: JSON response
    """
    values = json.loads(args)

    try:
        function = routes[values.get('function')]

        status = 'ok'
        res = function(values)
    except KeyError:
        status = 'fail'
        res = None

    return json.dumps({
        'status': status,
        'result': res,
    })


def greet(args):
    """Simple function that greets someone."""

    import sys;
    print(sys.version)

    print("Forcing a division by zero")
    try:
        1/0
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        #traceback.print_stack()
        #print(traceback.format_stack())
    print("Done exception test")

    import sqlite3
    try:
        conn = sqlite3.connect(":memory:")
        print(sqlite3.version)
    except Error as e:
        print(e)
        import traceback
        traceback.print_exc()
        #traceback.print_stack()
        #print(traceback.format_stack())
    finally:
        conn.close()
    print("Done sql test")

    try:
        import shutil
    except Error as e:
        print(e)
        import traceback
        traceback.print_exc()
        #traceback.print_stack()
        #print(traceback.format_stack())
    finally:
        conn.close()
    print("Done shutil test")

    result = 0
    try:
        import _main_widget
        result = _main_widget.show_question("a", "b", "c", "d")
    except Error as e:
        print(e)
        import traceback
        traceback.print_exc()
        #traceback.print_stack()
        #print(traceback.format_stack())

    return 'Tests done, received %d' % result


def add(args):
    """Simple function to add two numbers."""
    return args['a'] + args['b']


def mul(args):
    """Simple function to multiply two numbers."""
    return args['a'] * args['b']


routes = {
    'greet': greet,
    'add': add,
    'mul': mul,
}

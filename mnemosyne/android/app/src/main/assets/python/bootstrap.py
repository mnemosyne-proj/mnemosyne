#
# bootstrap.py
#

import json
try:
    from mnemosyne.android_python.mnemosyne_android import *
except Exception as e:
    import traceback
    traceback.print_exc()


def router(args):
    """Defines the router function that routes by function name.
    In and out args are in JSON format.

    """
    try:
        values = json.loads(args)
        print("router called with", values)
        function = routes[values.get('function')]
        res = function(values)
        status = "ok"
    except Exception as e:
        import io
        import traceback
        a = io.StringIO()
        traceback.print_exc(file=a)
        stack_trace = a.getvalue()
        print(stack_trace)
        res = stack_trace
        status = "fail"
    return json.dumps({
        'status': status,
        'result': res,
    })

routes = {
    "start_mnemosyne": start_mnemosyne,
    "pause_mnemosyne": pause_mnemosyne,
    "stop_mnemosyne": start_mnemosyne,
    "controller_heartbeat": controller_heartbeat,
    "config_get": config_get,
    "config_set": config_set,
    "config_save": config_save,
    "review_controller_show_answer": review_controller_show_answer,
    "review_controller_grade_answer": review_controller_grade_answer,
    "controller_show_sync_dialog_pre": controller_show_sync_dialog_pre,
    "controller_sync": controller_sync,
    "controller_show_sync_dialog_post": controller_show_sync_dialog_post,
    "controller_star_current_card": controller_star_current_card,
    "controller_show_activate_cards_dialog_pre": controller_show_activate_cards_dialog_pre,
    "controller_show_activate_cards_dialog_post": controller_show_activate_cards_dialog_post,
    "controller_set_study_mode_with_id": controller_set_study_mode_with_id,
    "controller_do_db_maintenance": controller_do_db_maintenance
}




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

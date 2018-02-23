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
    "controller_do_db_maintenance": controller_do_db_maintenance,
    "database_set_criterion_with_name": database_set_criterion_with_name
}

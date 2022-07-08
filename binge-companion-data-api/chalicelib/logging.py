import traceback


def return_traceback(func):
    try:
        return func
    except Exception:
        return {'error': traceback.format_exc()}

from markupsafe import Markup, escape

def nl2br(value):
    if value is None:
        return ''
    return Markup('<br>\n').join(escape(value).splitlines())

def parse_float(value, field_name, default=None, minimum=None):
    if value is None or str(value).strip() == '':
        if default is not None:
            result = float(default)
        else:
            raise ValueError(f"{field_name} is required")
    else:
        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be a valid number") from exc

    if minimum is not None and result < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}")
    return result

def get_list_value(values, index, default=''):
    if index < len(values):
        return values[index]
    return default

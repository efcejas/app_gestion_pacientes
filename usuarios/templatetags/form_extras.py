from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css):
    """Append CSS classes to a form field widget without losing existing ones."""
    existing = field.field.widget.attrs.get("class", "")
    combined = (existing + " " + css).strip()
    attrs = {**field.field.widget.attrs, "class": combined}
    return field.as_widget(attrs=attrs)


@register.filter(name="add_attrs")
def add_attrs(field, arg):
    """
    Set arbitrary HTML attributes on a form field widget.

    Usage in templates:
      {{ form.myfield|add_attrs:"id=file_input|aria-describedby=file_input_help|accept=image/png,image/jpeg" }}

    Pairs are separated by '|', and key/value by '='. The value may contain commas or slashes.
    If 'class' is provided, it will be merged with existing classes similar to add_class.
    """
    if not arg:
        return field
    attrs = dict(field.field.widget.attrs) if hasattr(field, 'field') else {}
    pairs = [p.strip() for p in str(arg).split('|') if p.strip()]
    for pair in pairs:
        if '=' not in pair:
            continue
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if key == 'class':
            existing = attrs.get('class', '')
            attrs['class'] = (existing + ' ' + value).strip()
        else:
            attrs[key] = value
    return field.as_widget(attrs=attrs)

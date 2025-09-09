from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css):
    """Append CSS classes to a form field widget without losing existing ones."""
    existing = field.field.widget.attrs.get("class", "")
    combined = (existing + " " + css).strip()
    attrs = {**field.field.widget.attrs, "class": combined}
    return field.as_widget(attrs=attrs)

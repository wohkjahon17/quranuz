from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    try:
        return d.get(key, 0)
    except Exception:
        return 0

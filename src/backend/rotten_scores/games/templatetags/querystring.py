from django import template
from django.http import QueryDict

from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def querystring(get_params: QueryDict, key: str, value: str | int) -> str:
    params = get_params.copy()
    params.setlist(key, [str(value)])

    query_items = []
    for k in params.keys():
        for v in params.getlist(k):
            query_items.append((k, v))

    return urlencode(query_items)

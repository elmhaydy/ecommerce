from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, fr_text, en_text):
    request = context.get("request")
    if request is None:
      return fr_text

    language = request.session.get("site_language", "fr")
    return en_text if language == "en" else fr_text

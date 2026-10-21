from django import template

register = template.Library()


@register.filter
def initials(user):
    """Zwei Initialen aus dem Anzeigenamen, ohne Zusätze in Klammern."""
    name = (getattr(user, "display_name", "") or getattr(user, "email", "") or "?").split("(")[0]
    parts = [p for p in name.replace("-", " ").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@register.filter
def role_tone(role):
    """Rollen sind kein Status: Projektleiter Logoblau, übrige Rollen Türkis."""
    return "tone-brand" if str(role) == "PROJEKTLEITER" else "tone-sky"

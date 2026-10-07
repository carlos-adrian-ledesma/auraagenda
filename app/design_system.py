"""AuraAgenda visual design tokens.

The values in this module deliberately avoid Qt imports so they can be audited and
tested in headless environments.  Widgets consume them through app.styles.
"""

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}

RADIUS = {
    "sm": 8,
    "md": 10,
    "lg": 12,
    "xl": 16,
}

SIZING = {
    "sidebar_width": 236,
    "topbar_height": 58,
    "control_min_height": 38,
    "button_min_height": 38,
    "settings_nav_width": 210,
    "form_max_width": 760,
    "content_max_width": 1180,
}

TYPOGRAPHY = {
    "page_title_pt": 22,
    "section_title_pt": 15,
    "card_title_pt": 12,
    "body_pt": 10,
    "caption_pt": 9,
}

# Required semantic tokens for every theme.  Keeping this list centralized stops
# a new theme from silently falling back to native Windows colours.
REQUIRED_THEME_TOKENS = {
    "bg1", "bg2", "sidebar", "surface", "surface_alt", "card", "border",
    "accent", "accent_hover", "accent2", "text", "muted", "disabled",
    "danger", "success", "dialog", "field", "paper", "ink", "selection_text",
}

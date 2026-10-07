# Visual Design System — AuraAgenda 2.0.3

## Goal

AuraAgenda uses one semantic visual system for the main window, pages, dialogs and first-run wizard. Dark themes must never depend on native Windows background colours.

## Core tokens

Defined in `app/design_system.py`:

- spacing: 4 / 8 / 12 / 16 / 24 / 32 px
- corner radii: 8 / 10 / 12 / 16 px
- sidebar: 236 px
- top bar: 58 px
- controls/buttons: approximately 36–42 px high
- settings category rail: 210 px
- normal form content is capped rather than stretched indefinitely

Theme-specific semantic colours live in `app/styles.py` and every theme must define background, sidebar, surfaces, cards, borders, accent, text, muted, disabled, danger, success, dialog and field colours.

## Layout rules

1. Pages use `Page` as their common shell with 24 px horizontal content margins.
2. Long settings sections and long dialogs use a scroll host; horizontal scrolling is avoided for forms.
3. Small forms cap field widths. Large monitors gain breathing room, not 1500-pixel text fields.
4. Tables use a compact row height, hidden row headers, dark headers and an interactive column layout.
5. Nested pages inside Finance/Wellness/Style hide redundant page headers.
6. Main navigation uses permanent page IDs. Group collapse only changes visibility, never stack indices.

## Reusable components

- `SectionCard`: bordered premium card with optional title/subtitle.
- `ScrollPage`: transparent scroll host with a capped content column.
- `Page`: common page header and spacing shell.
- semantic QPushButton variants through object names/properties (`Primary`, `Danger`, `variant=...`).

## Theme behaviour

The application stylesheet explicitly covers:

- main window / content shell
- sidebar / navigation groups / active navigation
- top bar / global search
- cards and group boxes
- line edits, text edits, combos, spin boxes, date/time controls
- combo popups and list views
- tabs
- tables/tree/list widgets and headers
- vertical/horizontal scrollbars
- calendar
- dialogs / message boxes / wizard / menus / tooltips
- diary paper special surface

When a theme changes, the global application stylesheet is regenerated from semantic tokens.

## Resolution strategy

The default window remains 1366×768 and can grow freely. The application minimum is 1024×640. Long settings and edit forms scroll rather than clipping. Form fields are width-capped. The sidebar has an independent scroll area and collapsible groups.

Actual Qt rendering at Windows DPI 100/125/150% still requires a Windows GUI smoke test; source-level layout invariants are covered by automated tests in this package.

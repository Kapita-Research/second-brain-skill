# JSON Canvas (.canvas)

A `.canvas` file is JSON following the [JSON Canvas 1.0 spec](https://jsoncanvas.org/spec/1.0/). Use it for visual thinking: mind maps, project boards, flowcharts, research layouts. Syntax verified against the spec and Obsidian behavior.

## Structure

```json
{ "nodes": [], "edges": [] }
```

## Nodes

Every node needs `id`, `type`, `x`, `y`, `width`, `height`. Array order = z-index (first = bottom).

| Field | Req | Notes |
|---|---|---|
| `id` | ✅ | unique 16-char lowercase hex, e.g. `"6f0ad84f44ce9c17"` |
| `type` | ✅ | `text` \| `file` \| `link` \| `group` |
| `x`,`y` | ✅ | integer px; top-left origin; can be negative |
| `width`,`height` | ✅ | integer px |
| `color` | – | preset `"1"`–`"6"` or hex `"#FF0000"` |

Type-specific required field:
- `text` → `text` (Markdown string; use `\n` for newlines — **never** literal `\\n`)
- `file` → `file` (vault-relative path); optional `subpath` (`#heading` or `#^block`)
- `link` → `url`
- `group` → optional `label`, `background`, `backgroundStyle` (`cover`|`ratio`|`repeat`)

```json
{ "id": "6f0ad84f44ce9c17", "type": "text", "x": 0, "y": 0,
  "width": 300, "height": 120, "text": "# Idea\n\nBody **markdown**." }
```

## Edges

| Field | Req | Default | Notes |
|---|---|---|---|
| `id` | ✅ | | unique |
| `fromNode` | ✅ | | source node id |
| `toNode` | ✅ | | target node id |
| `fromSide`/`toSide` | – | | `top`\|`right`\|`bottom`\|`left` |
| `fromEnd`/`toEnd` | – | `none`/`arrow` | `none`\|`arrow` |
| `color` | – | | preset or hex |
| `label` | – | | text on the edge |

```json
{ "id": "0123456789abcdef", "fromNode": "6f0ad84f44ce9c17",
  "fromSide": "right", "toNode": "a1b2c3d4e5f67890", "toSide": "left",
  "toEnd": "arrow", "label": "leads to" }
```

## Colors

`"1"` red · `"2"` orange · `"3"` yellow · `"4"` green · `"5"` cyan · `"6"` purple. (Exact shades are app-defined.) Omit for the default accent.

## ID generation

16-char lowercase hex (64-bit random), e.g. `"a3b2c1d0e9f8a7b6"`. Ensure uniqueness across **all** nodes and edges.

## Layout guidance

- Space nodes 50–100px apart; 20–50px padding inside groups; align to a 10/20px grid.
- Suggested sizes: small text 200–300×80–150; medium 300–450×150–300; file preview 300–500×200–400.

Common layouts:
- **Mind map / topic cluster** — central node at (0,0); spokes radiate ~600px out; edges center→spoke.
- **Project board (kanban)** — `group` nodes as columns (e.g. task statuses: Not Started / In Progress / Done), ~350px apart; `file` nodes pointing to task notes inside.
- **Pipeline / flow** — left→right, evenly spaced on x; edges right-side→left-side of next.
- **Hierarchy / tree** — root top-center; children below, y increases per level.

## Example — kanban board

```json
{
  "nodes": [
    { "id": "1111111111111111", "type": "group", "x": 0,   "y": 0, "width": 320, "height": 500, "label": "To Do",       "color": "1" },
    { "id": "2222222222222222", "type": "group", "x": 360, "y": 0, "width": 320, "height": 500, "label": "In Progress", "color": "3" },
    { "id": "3333333333333333", "type": "group", "x": 720, "y": 0, "width": 320, "height": 500, "label": "Done",        "color": "4" },
    { "id": "4444444444444444", "type": "file", "x": 20,  "y": 50, "width": 280, "height": 90, "file": "Work/Projects/Q3 Launch.md" },
    { "id": "5555555555555555", "type": "text", "x": 380, "y": 50, "width": 280, "height": 90, "text": "Draft landing page" }
  ],
  "edges": []
}
```

## Validate before delivering
1. All `id`s unique (nodes + edges).
2. Every `fromNode`/`toNode` references an existing node id.
3. Required fields present per node type.
4. `type` ∈ {text,file,link,group}; sides ∈ {top,right,bottom,left}; ends ∈ {none,arrow}.
5. Colors are `"1"`–`"6"` or valid hex.
6. JSON parses; text newlines are `\n` (not `\\n`).

References: https://jsoncanvas.org/spec/1.0/ · https://github.com/obsidianmd/jsoncanvas

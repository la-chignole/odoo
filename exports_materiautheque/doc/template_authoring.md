# Writing an export template

A template is a normal `.xlsx` file. The only thing this module adds is
`{{ }}` placeholders typed directly into cells.

To add metrics update files in `./models/metrics`. 

## 1. A single value

Type the metric's key in place of a value:

```
{{pos.recette_categorie}}
```

Available keys are whatever's registered in `models/metrics/*.py` (see
that module's `CLAUDE.md` to add one). `period.date_from`/`period.date_to`
(the export's own date range) are always available.

## 2. A repeating row

For "one row per record, however many there turn out to be" (one line per
stock move, per declaration entry, ...), mark a row: put, in any one
cell,

```
{{rows:block_name}}
```

That marker cell just flags the row and gets cleared — put it wherever
you don't need a real field. Every other cell on that row is a field
placeholder:

```
{{move.date}}   {{move.product}}   {{move.weight}}
```

The `move.` prefix is cosmetic — `{{date}}` and `{{move.date}}` are
identical. The row repeats once per record the metric returns, copying
its formatting to each copy.

Keep a rows-block at the bottom of its sheet (or on its own sheet) —
`insert_rows` doesn't renumber merged cells or formulas below it.

## 3. Scoping a value to specific tags or categories

Any tag/category filter is named directly in the cell:

```
{{stock.poids_par_tag_detail["Mat 1","Mat 2"]}}
```

A key with no bracket runs unfiltered, every time.

| Form | Meaning |
|---|---|
| `{{key}}` / `{{key[]}}` | no filter |
| `{{key["Mat 1","Mat 2"]}}` | tag filter, this cell only |
| `{{key[tag=["Mat 1"], pos_categ=["Meubles"]]}}` | tag **and** PoS category together |
| `{{rows:key["Mat 1","Mat 2"]}}` | repeating block, scoped to just these entries |
| `{{key["Mat 1"].field}}` | one field off the record matching "Mat 1", no row |
| `{{key["Mat 1","Mat 2"].field}}` | repeats the row once per named entry, in order |
| `{{key[].field}}` | same, but for every record the metric returns — `{{rows:key}}` spelled with `.field` |
| `{{key[A1].field}}` | name(s) read from cell A1 instead of typed here |

Names are quoted with `"` (double a literal `"`; apostrophes need no
escaping). Only two axes exist: `tag` and `pos_categ` — the same two
params every metric already accepts.

**Cell reference** (`A1`, `B12`, ...): the *same-sheet* cell's own text,
split on commas if it holds several (`Mat 1, Mat 2, Outils`). Lets a name
used by several cells in a row be typed once. The referenced cell can't
be a placeholder itself, and can't be empty.

**`.field`** reads a field off a list-returning metric without a
`{{rows:...}}` marker — the bracket's name count decides the shape:
- one name → a plain value (blank if that name has no data);
- several names (typed, or via a cell reference) → the row repeats once
  per name, in order;
- no name (`key[].field`) → the row repeats once per record the metric
  returns, dynamically.

Every `.field` placeholder sharing a repeating row must use the exact
same bracket (only `.field` differs), can't mix with an explicit
`{{rows:...}}` marker on that row, and must be a cell's entire content.

## 4. Building and checking a template

1. Lay out the file, type placeholders into the cells that need a value.
2. Save as `.xlsx`, upload it under **Exports ▸ Templates**. The form
   shows detected metric keys and row-blocks, with a warning if a bracket
   names a tag/category that doesn't exist.
3. Run it from **Exports ▸ Generate export** and check the numbers.

## 5. Making it a built-in, one-click report

Drop the `.xlsx` in `data/templates/` and restart the server.
A built-in can't be edited from the UI/CLI afterward; replace the file
and restart again to change it.

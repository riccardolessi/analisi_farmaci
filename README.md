# Drug Analysis App

A [Shiny for Python](https://shiny.posit.co/py/) application for browsing chemical assays
on molecules of pharmaceutical interest: outcome lookup, associated reagents, substructure
recognition via SMARTS (RDKit), and ML prediction of the bromine water assay. This app was part of my master's thesis, and i'm now updating it as a side project.

## Features

The interface is a navbar with seven tabs, one per Shiny module.

- **Search molecules** — pick a molecule and the list of assays narrows down to the ones
  actually performed on it; the button shows the recorded outcome
  (positive, negative).
- **Search assays** — the same path in reverse: start from the assay and get the list of
  molecules it was tested on, with the corresponding outcome.
- **Search reagents** — given a molecule, lists in a table the assays that involve it and,
  on request, the reagents each assay requires ("Assay X requires: ..."). Useful for
  preparing the bench before working on a molecule.
- **Pie chart** — interactive D3 sunburst, with hierarchy molecule type → molecule → assays
  with a positive outcome. The data is built in Python and passed to the chart via a custom
  message, with no extra HTTP calls.
- **Assay detail** — descriptive card for a single assay: name, reaction scheme (image from
  `assets/img_saggi`, with a fallback if missing), full description, and associated
  reagents.
- **Substructure recognition** — paste a SMILES and RDKit matches it against the SMARTS
  patterns stored for each assay, returning the list of assays expected to be positive.
  This is a structural prediction, not a statistical one: it depends only on the functional
  groups present in the molecule.
- **Bromine water assay prediction** — Random Forest model trained on Morgan fingerprints
  (radius 3, 1024 bits) of the dataset molecules: given a SMILES it returns a predicted
  outcome and a confidence percentage. Read it as an indication, not a definitive answer
  (see the model notes further below).

Across the board: invalid SMILES are reported instead of crashing the page, dropdowns are
populated from the database on every startup (no hard-coded lists), and each tab is an
independent Shiny module, so one can be added or removed without touching the others.

### Data available

| Content | Amount |
|---|---|
| Molecules, all classified into 12 types | 111 |
| Assays | 78 (78 detail cards) |
| Recorded molecule × assay outcomes | 1190, of which 740 positive |
| Reagents and assay-reagent associations | 54 reagents, 108 associations |
| Assays with a SMARTS pattern for recognition | 67 out of 78 |
| Illustrated reaction schemes | 28 assays, 30 images |

## Getting started

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
shiny run --reload app.py
```

> The app must be launched **from the project root**: the database and assets are
> referenced with relative paths (`analisi_farmaci.db`, `assets/img_saggi/...`).

## Structure

| Path | Role |
|---|---|
| `app.py` | Entry point: navbar + module registration |
| `modules/` | One Shiny module per tab (search molecules, search assays, reagents, sunburst, assay detail, substructures, ML prediction) |
| `query.py` | All SQLite queries (data layer) |
| `db.py` | Database schema creation |
| `riconoscimento_sottostrutture.py` | SMARTS matching with RDKit |
| `train_ml.py` | Random Forest training → `modello.pkl` |
| `script.js` | D3 sunburst fed via `session.send_custom_message("d3data", ...)` |
| `analisi_farmaci.db` | SQLite database (111 molecules, 76 assays, 78 saggi_new, 1190 outcomes) |

## Regenerating derived files

```bash
python db.py
```

```bash
python train_ml.py
```

`db.py` creates the schema but does not repopulate the data; `train_ml.py` retrains the
Random Forest and rewrites `modello.pkl`. The model is tied to the scikit-learn version it
was saved with: after a package upgrade it needs to be retrained, otherwise `pickle.load`
fails with a dtype error.

---

# Possible improvements

Review notes, ordered by value-to-cost ratio. The app works: what follows is about
robustness, maintainability, and reliability of the results.

## Data access (`query.py`)

- **A single connection point.** Right now there are about twenty scattered
  `sqlite3.connect('analisi_farmaci.db')` calls, with a relative path: the app only works
  if launched from the root. A configuration module with
  `DB_PATH = Path(__file__).parent / "analisi_farmaci.db"` and a `get_conn()` context
  manager would remove the working-directory constraint, always close the connection
  (`reagenti_da_saggio` is missing a `close()`), and be the right place to enable
  `PRAGMA foreign_keys = ON`.
- **Rows as objects, not tuples.** The code reads by index everywhere (`esito[3]`,
  `saggio[1]`, `mol[2]`, `saggio_details[5]`): changing the order of a column, or running a
  `SELECT *` on a modified table, is enough to make the app show the wrong data with no
  error at all. `conn.row_factory = sqlite3.Row`, or small domain dataclasses (`Molecola`,
  `Saggio`, `Esito`), would make the code self-explanatory and resistant to schema changes.
- **Errors: exceptions, not status dictionaries.** Functions return dicts whose `status` is
  by turns `success`, `failed`, `message`, `error`, and the UI passes it straight to
  `ui.notification_show(type=...)`, which only accepts some of those values. Better to raise
  domain exceptions and translate them into notifications in a single helper.

## Database integrity

- **Foreign keys are not enforced.** SQLite ignores them until `PRAGMA foreign_keys = ON` is
  enabled on every connection: today the `ON DELETE CASCADE` clauses declared in `db.py` are
  decorative. There are currently no orphan rows, so the pragma can be turned on safely.
- **`esiti_saggi` has neither constraints nor indexes.** No FK to `molecole` or `saggi`, no
  `UNIQUE(id_molecola, id_saggio)`: there are already **11 duplicate pairs**. A unique
  index, after a one-off deduplication, would stop the displayed outcome from depending on
  which row comes back first.
- **Outcome semantics need to be fixed.** The values are `POSITIVO`, `NEGATIVO`, `DUBBIO`,
  and `INFO`, but `ottieni_saggi_positivi()` filters `!= 'NEGATIVO'` (so DUBBIO and INFO
  count as positive in the sunburst) while `ricerca_complessa()` uses `= 'POSITIVO'`. One
  single rule is needed, ideally made explicit through a lookup table or a `CHECK`
  constraint.
- **Schema debt.** The `desrizione` typo in `saggi_new`, `molecole.tipologia_id` typed as
  `TEXT` while referencing an `INTEGER`, the leftover `saggi_reagenti_old` table: fixable
  only through a data migration, not by rewriting `db.py`.
- **A migration mechanism is needed.** `db.py` knows how to create the schema from scratch,
  not how to update it: any change applied by hand to the `.db` file leaves no trace. A
  `migrations/` folder with numbered scripts, or a lightweight tool like
  `yoyo-migrations`, would make the schema's evolution reproducible.

## Shiny modules

- **`@render.image` nested inside a `@reactive.effect`** in `dettaglio_saggi.py`: the output
  is only registered on the first click and re-registered on every subsequent one. The
  correct pattern is a `reactive.Value` holding the image path and a render declared at
  module level.
- **Side effect inside a render.** In `cerca_reagenti.py`, `ui.update_action_button()` is
  called inside `@render.data_frame`; also, `val = reactive.Value()` has no initial value,
  so the next render depends on click order.
- **`cerca_molecole` and `cerca_saggi` are the same module in two directions**, with
  different quality: one handles errors and guides the user, the other doesn't. A single
  parameterized module would halve the code and make the experience consistent.
- **`dettaglio_saggi.py` opens SQLite on its own** (`cerca_saggi()`): it's the only place
  that bypasses `query.py`, and should be brought back into the data layer.
- **`riconoscimento_sottostrutture.py` in the root has the same name as the Shiny module**
  that imports it

## Testing and automation

- **No tests.** At the moment no testing of database reads and writes has been implemented
  yet.
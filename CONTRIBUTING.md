# Contributing

Useful contributions make the analysis easier to understand, more reproducible, or more faithful to the evidence. Corrections to calculations, source interpretations, and unclear writing are welcome.

## Start with the finding

Describe the question or error, the relevant notebook section, and the evidence supporting the change. For a disputed annotation, include the reading ID and explain how the passage supports an alternative interpretation. Do not infer the reviewer's background, motivations, or behavior from a label alone.

Keep observations separate from interpretations. A keyword match is not a complaint, an NMF assignment is not a validated topic label, and an overall recommendation is not a story rating.

## Work locally

Use Python 3.12 and install the environment described in the [README](README.md). After changing analysis code or the notebook, run:

```bash
python scripts/run_notebook.py
python -m unittest discover -s tests -v
```

For changes to model fitting or stability calculations, also run:

```bash
python scripts/check_model_stability.py
```

Keep notebook outputs and figures consistent with the code. Explain any change to a published number, denominator, label, or conclusion. Avoid adding dependencies when a clear solution is already available in the existing environment.

Edit `notebooks/wukong_player_experience.py`, the readable cell-based source, then use the runner to rebuild the `.ipynb` and HTML outputs. This keeps the narrative, code, and saved results together.

## Preserve the data boundary

The repository distributes prepared features, model inputs, and short attributed excerpts. Do not add full review texts, raw API responses, local environments, credentials, or unrelated personal files.

Do not overwrite this snapshot with a fresh collection and leave its dates or findings unchanged. A new snapshot needs its own provenance, integrity checks, and reviewed narrative. Changes to preprocessing require the original full-text source and a new export; the public matrix alone cannot establish that a preprocessing change was applied correctly.

If you have the original saved project, the export command is:

```bash
python scripts/prepare_public_data.py --source-root <path-to-original-project>
```

This recreates exports from existing local data. It does not scrape Steam.

## Write for readers

Use plain English, short code cells, and comments that explain why a step matters. Define the denominator next to a percentage. Prefer a concrete research question over an unsupported recommendation to change the game.

Document AI assistance in code, writing, or annotations when it is relevant to a contribution. Do not mark a label as independently reviewed unless someone actually reviewed it independently and the review process is recorded.

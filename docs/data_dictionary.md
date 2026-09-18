# Data dictionary

All files describe the saved September 17, 2026 collection. Dates are UTC. A review is an observation about the whole game; a recommendation flag is not an aspect-level sentiment label.

## `data/review_features.csv`

**Grain:** one row per distinct Steam review ID. **Rows:** 8,200. Blank and short texts remain represented. Full review text and author profile IDs are not included in this table.

| Field | Meaning |
|---|---|
| `review_id` | Steam review identifier. Read as a string, not a measurement. Unique within this table. |
| `created_utc` | Time the review was created. Determines inclusion in the study window and creation cohort. |
| `updated_utc` | Last-update timestamp observed at collection. Text and recommendation may have changed since creation. |
| `recommended` | Boolean overall Steam recommendation observed at collection: true means recommended. |
| `word_count` | Word tokens after lowercase, link/markup removal, and whitespace normalization. Unchecked template options remain in this descriptive count. |
| `playtime_hours` | Playtime recorded at review time, converted from minutes to hours. Not current lifetime playtime. |
| `story_match` | Boolean match to the exploratory story vocabulary. Not a verified story label or sentiment. |
| `world_match` | Boolean match to the exploratory world vocabulary. Not a verified world-building label or sentiment. |
| `emotion_match` | Boolean match to the exploratory emotion vocabulary. Does not identify a feeling or its trigger. |
| `keyword_match` | Boolean union of the three vocabulary flags. A review is counted once even if several groups match. |
| `topic_id` | Largest-weight vocabulary component, `T1`–`T8`, or a modeling exclusion status. Not a verified experience category. |

The modeling exclusions distinguish `Under 20 usable words`, `Script screening exclusion`, and `Insufficient vocabulary`. The modeling word count differs from `word_count` because unchecked checklist lines are removed only from the model copy.

## `data/evidence.csv`

**Grain:** one selected review. **Rows:** 24, consisting of 12 recommending and 12 non-recommending older keyword matches. These are discovery cases, not a representative sample.

Each excerpt is at most 25 words from one source review. Full review texts are excluded.

| Field | Meaning |
|---|---|
| `reading_id` | Stable display identifier, `H01`–`H24`. |
| `review_id` | Source review identifier; joins to `review_features.csv`. |
| `created_utc` | Creation timestamp from the saved source. |
| `recommendation` | Human-readable `Recommended` or `Not recommended`. |
| `relevance` | Assistant judgment: `yes`, `no`, or `unclear`. |
| `story_sentiment` | Assistant's aspect-level story assessment. |
| `world_sentiment` | Assistant's aspect-level world assessment. |
| `emotional_trigger` | Event or aspect linked to a reported response, when identified. |
| `evidence` | Short verbatim excerpt from the source review. |
| `interpretation` | Assistant's reading of the evidence, including uncertainty where relevant. |
| `review_url` | Public Steam source link. The live text may change or disappear. |
| `annotator` | `assistant`; identifies label authorship. |
| `independent_review` | `False` for these records; they have not been independently human-validated. |

Label meanings:

| Label | Interpretation |
|---|---|
| Relevance: `yes` | The assistant identified an explicit story, world, or event-linked emotional experience. |
| Relevance: `no` | A vocabulary match did not establish a relevant experience under the study's definitions. |
| Relevance: `unclear` | Meaning, language, or the evidence was insufficient for a confident relevance judgment. |
| Story/world sentiment: `positive`, `negative`, `mixed`, `neutral` | The assistant's aspect-specific interpretation. These labels do not override overall recommendation. |
| Story/world sentiment: `unclear` | The aspect is mentioned but its assessment is ambiguous. |
| Story/world sentiment: `not assessed` | The review does not support an aspect-level judgment in this annotation. This is not neutral sentiment. |
| Emotional trigger | The event or aspect linked to a reported response, when identified. Generic praise or dislike alone does not establish narrative emotion. |
| Interpretation | A brief reading of the evidence, including uncertainty where relevant. Not a verified product fact. |
| Annotator / independent-review status | Attribution to the assistant and disclosure that the labels are not independent human validation. |

H12 is predominantly Thai despite Steam's English tag; it is not used to support English-language narrative conclusions. H07 has a translation-style preface whose provenance was not verified.

## Prepared model inputs

| File | Content and alignment |
|---|---|
| `data/model/tfidf.npz` | Sparse TF-IDF matrix, **2,489 rows × 7,651 features**. Load with `scipy.sparse.load_npz`. Values are nonnegative feature weights, not term counts or sentiment scores. |
| `data/model/review_ids.csv` | Review ID corresponding to each matrix row, in matrix order. Do not sort independently of the matrix. |
| `data/model/vocabulary.json` | Terms corresponding to matrix columns. Preserve column alignment when displaying fitted components. |
| `data/model/metadata.json` | Modeling configuration, recorded reference results, and provenance needed to interpret the prepared inputs. |
| `data/model/topic_names.json` | Working analyst names and interpretations for `T1`–`T8`. These are not validated category definitions. |
| `data/model/topic_reference.json` | Saved component summaries used as reference results, including vocabulary and assignment counts. |

The preparation used unique normalized texts for fitting. The supplied matrix supports model refitting but does not substitute for raw text when evaluating preprocessing choices.

## Provenance and integrity

| File | Purpose |
|---|---|
| `data/provenance.json` | Collection scope, export context, and the boundary between included prepared inputs and the original local source collection. |
| `data/checksums.json` | SHA-256 checksums for included inputs. Detects unexpected file changes; a matching hash does not establish semantic accuracy. |
| `data/pilot_evaluation.json` | Reference metrics from the earlier 40-review assistant evaluation. This is separate from the 24 discovery cases and is not an independent benchmark for the full collection. |

See the [methodology](methodology.md) for exact keyword definitions, modeling choices, and what can be reproduced from these files.

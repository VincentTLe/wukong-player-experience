# Methodology

## Question and unit of analysis

The study asks how public reviews can reveal useful research questions about Black Myth: Wukong's story, world, and player experience.

One observation is **one Steam review ID**, not one game owner or one play session. Distinct IDs with identical text remain distinct observations in descriptive counts. Public reviewers are a selected population; the collection does not represent all players.

## Collection and scope

- **Source:** Steam reviews API, application `2358720`.
- **Creation window:** September 17, 2025, 00:00 UTC, inclusive, to September 17, 2026, 00:00 UTC, exclusive.
- **Collection began:** September 17, 2026, 06:00:30 UTC.
- **Filters:** English tag, both recommendation types, all purchase types, most recent first, 100 reviews per page, off-topic activity filtering disabled.
- **API parameters:** `json=1`, `filter=recent`, `language=english`, `review_type=all`, `purchase_type=all`, `num_per_page=100`, `filter_offtopic_activity=0`.

The collector followed cursors until it crossed the lower date boundary. It saved **83 pages containing 8,298 unique review IDs**. Excluding 95 records before the window and three at or after its end leaves **8,200 reviews**. Saved-page checks covered hashes, ordering, duplicates, and reconciliation to the processed collection. These checks were performed in the original local project; this public repository includes a provenance record, not the raw pages.

A changing API cannot provide an immutable census during collection. Review text and recommendation reflect the snapshot at collection time, even when a review was created months earlier. Grouping by creation date therefore does not reconstruct past rating states.

The API documentation defines the source fields and filters: [Steam user reviews documentation](https://partner.steamgames.com/doc/store/getreviews).

## Data quality

The original collection has **34 blank texts**, **682 reviews edited after creation**, and no missing playtime-at-review values. After basic text normalization there are **1,579 duplicate-text excess records**; they are not automatically deleted because their review IDs are distinct.

The English tag is imperfect. One close-reading example, H12, is predominantly Thai. Its uncertainty is recorded, and it does not support the English-language narrative conclusions. H07 contains a translation-style preface; the actual authorship process is unknown.

The public feature table preserves all 8,200 IDs, including short and blank reviews. No current lifetime playtime is substituted for playtime recorded at the time of the review.

## Descriptive comparisons

### Recommendation

Recommendation rate is the number of recommending reviews divided by the number of reviews in the stated group. The full collection contains 7,408 recommending and 792 non-recommending reviews.

The two adjacent comparison periods are equally long:

| Creation cohort | Reviews | Recommended | Rate |
|---|---:|---:|---:|
| March 21–June 18, 2026 | 1,673 | 1,536 | 91.8% |
| June 19–September 16, 2026 | 2,286 | 2,029 | 88.8% |

Their difference is descriptive. Neither timing nor review text establishes an effect of a patch, a sale, a particular mechanic, or a narrative problem.

### Keyword retrieval

The original baseline uses case-insensitive, whole-word patterns:

| Group | Terms and variants |
|---|---|
| Story | story, stories, storytelling, plot, lore, narrative, narration, cutscene(s), ending(s), character(s) |
| World | world, worldbuilding, world-building, atmosphere, atmospheric, immersive, immersion, immersed |
| Emotion | emotional, emotionally, moving, moved, cry, crying, tears, heartbreaking, touching, goosebumps, nostalgia, nostalgic |

A review is a keyword match when at least one group matches. These overlapping flags are calculated on original text, including any template alternatives. They are retrieval signals, not sentiment or verified topic labels. For example, “character” can mean a controllable avatar, and “cutscene” can appear in a performance complaint.

The public repository includes the resulting flags, not the full texts needed to recompute them. The original pilot's 40-review assistant evaluation is separate from this public analysis and does not validate the expanded collection independently.

### Review length and the aggregate reversal

The word count uses lowercase text after removing markup and links and normalizing whitespace. It counts word tokens with `\b\w+\b`. Unchecked template alternatives remain in this descriptive text copy. This is a consistent operational measure of length, not a linguistic count of meaningful words.

Length bands are under 20, 20–79, 80–199, and 200 or more words. Keyword match rates are reported for each recommendation group within each band. The overall comparison reverses in every band.

For standardization, each band's match rate is weighted by that band's share of all 8,200 reviews. The same weights are applied to both recommendation groups. The resulting rates describe a common length mix; they do not identify a causal effect. Broad bands still allow differences in length, format, and content within them.

## Close reading

The original local analysis selected 24 keyword-matching reviews outside the initial 90-day pilot: 12 recommending and 12 non-recommending. Within each recommendation group, reviews were ordered by a SHA-256 hash of `history-reading-v1:` followed by the review ID; the first 12 were selected.

The assistant read the full texts and recorded relevance, story sentiment, world sentiment, emotional trigger, evidence, and interpretation. The public evidence file includes attributed excerpts of at most 25 words per review and links to the original sources. Labels such as “unclear” and “not assessed” are retained.

This is a discovery sample. It does not estimate the prevalence of themes, and selecting only keyword matches can miss relevant reviews without those words. Balanced recommendation groups do not reflect the recommendation distribution of the collection. The same assistant contributed to methods and interpretation, so these labels are not an independent human benchmark.

The conclusions distinguish what a reviewer reported from what the study establishes. Statements about developer motives, patch effects, technical causes, or intended replay are not verified facts or observed behavior.

## Exploratory text model

### Preparation

Model preparation uses a separate copy of the text. It removes unchecked checklist lines beginning with `☐`, then applies the basic cleaning described above. Original review text is unchanged.

The screen requires at least 20 usable word tokens and at least 80% ASCII letters among alphabetic characters. The latter detects some script mismatches; it **does not establish English language** and can admit other languages written in the Latin alphabet.

The exclusions are:

| Modeling status | Reviews |
|---|---:|
| Under 20 usable words | 5,669 |
| Longer texts failing the script screen | 22 |
| Fewer than five retained vocabulary features | 20 |
| Assigned to a vocabulary group | 2,489 |
| **All reviews** | **8,200** |

Short and excluded texts remain in descriptive denominators. Fitting uses one copy per normalized text. In this snapshot, the final fitting matrix contains 2,489 rows and 7,651 features.

### TF-IDF and NMF

TF-IDF represents texts using words and two-word phrases, giving more weight to terms that distinguish documents. Settings include `min_df=3`, `max_df=0.85`, `max_features=12000`, `ngram_range=(1, 2)`, and `sublinear_tf=True`, with scikit-learn's English stop words plus a recorded list of generic game and praise terms.

Non-negative matrix factorization (NMF) approximates this matrix with a smaller set of recurring vocabulary patterns. The primary fit has eight components, random initialization, seed 42, `max_iter=600`, and `tol=0.0001`. Eight groups were chosen for readable exploration; they are not a verified number of player concerns.

Before comparing each review's component weights, the analysis accounts for the arbitrary scaling of NMF components and normalizes the weights. A largest-weight assignment supports navigation. The weights are not probabilities, and the names assigned to components are analyst interpretations of vocabulary.

The public matrix allows the model to be refit without distributing full review texts. Matrix rows align with `data/model/review_ids.csv`; columns align with `data/model/vocabulary.json`. Configuration and reference diagnostics are stored in `data/model/metadata.json`.

### Stability and limits

Alternative seeds 7 and 19 test dependence on initialization. Components are matched by vocabulary cosine similarity, and dominant document assignments are compared with adjusted Rand index (ARI). These are stability measures, not semantic accuracy scores.

Seed 7 closely reproduces the main model. Seed 19 yields an assignment ARI of approximately **0.714**, while the matched cosine for the Journey to the West/fandom component falls to **0.071**. That component should be treated particularly cautiously.

Fits with six, eight, and ten components have relative reconstruction errors of approximately 0.9779, 0.9748, and 0.9721. Additional components are expected to reduce error; this does not demonstrate better interpretations. The high residual indicates that the small model leaves much vocabulary variation unexplained.

A numeric-rating component is a review-format pattern, not a player need. No group count is presented as a verified complaint or experience count. See [scikit-learn's topic extraction example](https://scikit-learn.org/1.7/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html) for the underlying modeling approach.

## What can be reproduced

From the public repository, without network requests or credentials, a reader can:

- Verify included-file checksums and review-level counts.
- Recalculate recommendation, keyword, period, and length comparisons.
- Recreate figures and execute the main notebook.
- Refit NMF from the prepared TF-IDF matrix and repeat the recorded stability checks.
- Inspect short attributed evidence excerpts and the assistant's interpretations.

The repository does **not** include full reviews or raw API responses. A reader cannot independently rebuild preprocessing, verify every raw page, or reassess full-text annotations using the public inputs alone. Steam links provide attribution, but live reviews can change or disappear.

For a contributor who has the original saved project, `scripts/prepare_public_data.py --source-root <path>` recreates public exports from that local source. It is not a fresh network scrape. Recollecting Steam reviews would produce a new snapshot and would require renewed checks, labels, and written conclusions.

## AI assistance and interpretation

The project's code, analysis, prose, and recorded annotations were developed with AI assistance. The author is responsible for reviewing and owning final interpretations. The work does not claim independent human annotation, a validated sentiment classifier, a causal effect, or a predicted commercial outcome.

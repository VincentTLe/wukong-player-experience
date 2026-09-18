# Beyond the Thumbs-Up

## The question

**What can public reviews help us investigate about Black Myth: Wukong's story and world?**

The aim is to move from a broad rating—recommended or not recommended—to specific experiences: following the plot, enjoying the storytelling, feeling immersed, or becoming frustrated by combat. Those experiences can coexist in the same review.

The evidence is a snapshot of **8,200 English-tagged Steam reviews created September 17, 2025–September 16, 2026 UTC**, collected September 17, 2026. It describes these reviews, not all players.

## 1. Enjoying the story is different from understanding it

One recommending reviewer writes:

> I didn’t always catch the whole plot, but overall I liked the story.

— [H16, review 223328169](https://steamcommunity.com/profiles/76561198992854945/recommended/2358720/)

Another reviewer praises the adaptation and cutscenes but does not recommend the game because of frustrating mechanics. [H08, review 208970264](https://steamcommunity.com/profiles/76561198027961613/recommended/2358720/)

These are contrasting examples, not estimates of how often either experience occurs. They show why a single recommendation flag cannot stand in for story enjoyment, comprehension, or emotional attachment.

**Research implication:** ask separately what players understood, what they enjoyed, and what prompted their overall recommendation.

## 2. A simple keyword count almost tells the wrong story

Across the full collection, story, world, or emotion keywords appear in:

| Overall recommendation | Keyword matches | Reviews | Match rate |
|---|---:|---:|---:|
| Not recommended | 225 | 792 | 28.4% |
| Recommended | 1,289 | 7,408 | 17.4% |

It would be easy to conclude that these topics are associated with dissatisfaction. But within **all four review-length bands**, the recommending group has the higher match rate.

![Keyword match rates overall and within review-length bands.](../reports/figures/length_reversal.png)

Longer reviews have more opportunities to mention a topic, and the recommendation groups have different length distributions. Giving both groups the same four-band length mix produces descriptive match rates of **14.0% for non-recommending reviews and 19.4% for recommending reviews**.

This comparison does not show that narrative experiences cause a recommendation. It shows why review composition matters. Keywords also do not distinguish praise from criticism.

**Research implication:** inspect the source text and the denominator before interpreting a count as evidence of a product problem.

## 3. Specific comments suggest better research questions

The assistant read a separate discovery sample of **24 older keyword-matching reviews: 12 recommending and 12 non-recommending**. The sample was selected reproducibly, but its balanced design and keyword filter make it unsuitable for estimating prevalence.

| Observation in the selected reviews | Evidence | Next research question |
|---|---|---|
| Appreciation of cinematics can coexist with missing chapter context. | H04 praises chapter cinematics but describes abrupt changes of setting; H16 enjoys the story despite gaps in understanding. | At a chapter opening, can players explain where they are, their immediate objective, and how they arrived? |
| Visual beauty does not guarantee uninterrupted immersion. | H23 recommends the game but describes invisible walls breaking immersion; H15 explicitly praises world-building. | Where do players' expectations of explorable space differ from what the game permits? |
| Strong emotion may come from combat rather than narrative. | H20 describes satisfaction from overcoming bosses; H08 praises storytelling while rejecting frustrating mechanics. | Which event triggered a feeling: the story, a fight, or exploration? |

The cases are linked in [the evidence table](../data/evidence.csv). These questions are proposed for investigation; they are not a ranking of confirmed defects, severity, or business value.

## Supporting context

Overall recommendation is **7,408/8,200 = 90.3%**. Among the most recent 90-day creation cohort, it is **2,029/2,286 = 88.8%**, compared with **1,536/1,673 = 91.8%** in the preceding 90 days. The difference is **−3.05 percentage points**. Ratings and texts are observed at collection time, and the analysis does not explain the difference.

An eight-group text model organizes **2,489 reviews with enough retained vocabulary for modeling**. It helps find contrasting passages, but the group closest to Journey to the West and fandom changes substantially under one alternative initialization. Model assignments should not be treated as verified sentiment or experience categories.

## What the project contributes

The result is a set of traceable research leads and a worked example of careful interpretation: **start with a broad signal, check whether the comparison is fair, and return to what people actually wrote.**

The next useful step would be structured interviews or play observation that measure comprehension, enjoyment, and the event behind each emotion separately. This study does not estimate the prevalence of narrative problems, prove a cause of dissatisfaction, or forecast retention or revenue.

Read the [complete notebook](../notebooks/wukong_player_experience.ipynb) for calculations and figures, or the [methodology](methodology.md) for assumptions and reproducibility limits.

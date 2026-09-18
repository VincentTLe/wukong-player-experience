"""Create the small publication bundle from the verified local research archive.

This command does not scrape Steam or copy the archive wholesale. Original text and
author metadata stay in the archive; only allowlisted features and short quotations
are exported. The source project is needed only to rebuild these prepared inputs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main(source_root):
    source_root = source_root.resolve()
    sys.path.insert(0, str(source_root/'scripts'))
    from analyze_history import read_verified_history, clean_text, latin_share, EXTRA_STOP_WORDS
    original, collection = read_verified_history()
    history = source_root/'reports/history'
    enriched = pd.read_csv(history/'reviews_enriched.csv',dtype={'review_id':str},keep_default_na=False)
    assert original.review_id.tolist() == enriched.review_id.tolist()
    output = ROOT/'data'
    (output/'model').mkdir(parents=True,exist_ok=True)

    # Explicit allowlist prevents accidental publication of names, account IDs, or full text.
    columns = ['review_id','created_utc','updated_utc','voted_up','word_count','playtime_hours',
               'story_match','world_match','emotion_match','candidate','topic_id']
    features = enriched[columns].rename(columns={'voted_up':'recommended','candidate':'keyword_match'})
    features.to_csv(output/'review_features.csv',index=False,lineterminator='\n')

    readings = pd.read_csv(history/'reading_24_assistant.csv',dtype={'review_id':str},keep_default_na=False)
    columns = ['reading_id','review_id','created_utc','recommendation','relevance','story_sentiment',
        'world_sentiment','emotional_trigger','evidence','interpretation','review_url','annotator','independent_review']
    evidence = readings[columns].copy()
    # Keep the object of this claim in the quotation, so it makes sense on its own.
    evidence.loc[evidence.reading_id.eq('H23'), 'evidence'] = (
        'I hated the amount of invisible walls; it was nauseating, and it broke the immersion.')
    original_text = readings.set_index('review_id').review
    assert all(row.evidence in original_text.loc[row.review_id] for row in evidence.itertuples())
    assert all(len(re.findall(r"\b\w+\b",text)) <= 25 for text in evidence.evidence)
    evidence.to_csv(output/'evidence.csv',index=False,lineterminator='\n')

    # Share numeric text features, not a second copy of thousands of authored reviews.
    text = original.review.map(lambda value: clean_text(value, omit_unchecked=True))
    enough_words = text.str.findall(r'\b\w+\b').str.len().ge(20)
    script_screen = text.map(latin_share).ge(0.8)
    fit_rows = pd.DataFrame({'review_id':original.review_id,'text':text})
    fit_rows = fit_rows.loc[enough_words & script_screen].drop_duplicates('text')
    vectorizer = TfidfVectorizer(stop_words=sorted(set(ENGLISH_STOP_WORDS)|EXTRA_STOP_WORDS),
        min_df=3,max_df=0.85,max_features=12000,ngram_range=(1,2),sublinear_tf=True)
    matrix = vectorizer.fit_transform(fit_rows.text)
    usable = matrix.getnnz(axis=1) >= 5
    matrix,fit_rows = matrix[usable],fit_rows.loc[usable]
    assert matrix.shape == (2489,7651)
    save_npz(output/'model/tfidf.npz',matrix)
    fit_rows[['review_id']].to_csv(output/'model/review_ids.csv',index=False,lineterminator='\n')
    write_json(output/'model/vocabulary.json',vectorizer.get_feature_names_out().tolist())
    write_json(output/'model/metadata.json',json.loads((history/'model.json').read_text(encoding='utf-8')))
    write_json(output/'model/topic_names.json',json.loads((history/'topic_names.json').read_text(encoding='utf-8')))
    write_json(output/'model/topic_reference.json',json.loads((history/'topics.json').read_text(encoding='utf-8')))

    pilot = json.loads((source_root/'reports/evaluation.json').read_text(encoding='utf-8'))
    write_json(output/'pilot_evaluation.json',pilot)
    audit = json.loads((history/'audit.json').read_text(encoding='utf-8'))
    provenance = dict(app_id=2358720,game='Black Myth: Wukong',
        provider='Steam Reviews API',documentation=collection['api_documentation'],
        collected_at_utc=collection['collected_at_utc'],finished_at_utc=collection['finished_at_utc'],
        window_start_utc=collection['window_start_utc'],window_end_exclusive_utc=collection['window_end_exclusive_utc'],
        parameters=collection['parameters'],coverage=collection['coverage'],reconciliation=collection['reconciliation'],
        original_processed_sha256=collection['processed_sha256'],
        raw_page_hashes=[row['sha256'] for row in collection['raw_pages']],audit=audit,
        prepared_at_utc=datetime.now(timezone.utc).isoformat(),
        unit='One review ID, not one player or one purchase.',
        reproducibility='Published numeric inputs reproduce descriptive analysis and model fitting. Rebuilding text features or checking the full context of annotations requires the original local raw archive; live review URLs may change.',
        label_authorship='Assistant; not independently human-validated.',
        text_export='Short attributed excerpts only. Full texts and raw author metadata are not part of this bundle.')
    write_json(output/'provenance.json',provenance)
    files = [path for path in output.rglob('*') if path.is_file() and path.name!='checksums.json']
    checksums = {path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}
    write_json(output/'checksums.json',checksums)
    print(f'Prepared {len(features):,} review rows, {len(evidence)} short evidence records, and {matrix.shape} text matrix.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,required=True,help='Existing steam-feedback research archive')
    main(parser.parse_args().source_root)

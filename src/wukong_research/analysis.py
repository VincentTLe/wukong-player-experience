"""Data checks and calculations shared by the notebook and verification scripts."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

LENGTH_BANDS = ['Under 20 words','20–79 words','80–199 words','200+ words']


def verify_data(root):
    """Fail clearly if a prepared input differs from the published version."""
    root = Path(root)
    checksums = json.loads((root/'data/checksums.json').read_text(encoding='utf-8'))
    for relative_path,expected in checksums.items():
        actual = hashlib.sha256((root/relative_path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Input checksum mismatch: {relative_path}')
    return len(checksums)


def load_reviews(root):
    reviews = pd.read_csv(Path(root)/'data/review_features.csv',dtype={'review_id':str})
    reviews['created_utc'] = pd.to_datetime(reviews.created_utc,utc=True)
    reviews['length_band'] = pd.cut(reviews.word_count,[-1,19,79,199,np.inf],labels=LENGTH_BANDS)
    reviews['recommendation'] = reviews.recommended.map({True:'Recommended',False:'Not recommended'})
    return reviews


def match_rates(reviews,group_by):
    counts = reviews.groupby(group_by,observed=True).agg(
        reviews=('review_id','size'),matches=('keyword_match','sum'))
    counts['match_rate'] = counts.matches/counts.reviews
    return counts


def scale_adjusted_weights(weights,components):
    """NMF component scale is arbitrary; remove it before choosing the largest weight."""
    adjusted = weights*np.linalg.norm(components,axis=1)
    total = adjusted.sum(axis=1,keepdims=True)
    return np.divide(adjusted,total,out=np.zeros_like(adjusted),where=total!=0)

"""Refit the published text matrix and check how much the topic map changes.

Run from any directory: python scripts/check_model_stability.py
No network requests or original review archive are needed. These diagnostics
measure numerical stability, not whether the topics are semantically correct.
"""
import json
from pathlib import Path
import platform
import sys
import warnings

import numpy as np
import pandas as pd
import scipy
from scipy.optimize import linear_sum_assignment
from scipy.sparse import load_npz
import sklearn
from sklearn.decomposition import NMF
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics.pairwise import cosine_similarity
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from wukong_research.analysis import scale_adjusted_weights, verify_data


def fit_model(matrix, components, seed):
    """Keep every fit on the same recorded settings and retain any warnings."""
    model = NMF(n_components=components, init='random', random_state=seed,
                max_iter=600, tol=0.0001)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        weights = model.fit_transform(matrix)
    return model, weights, [str(item.message) for item in caught]


def describe_fit(model, terms, messages, matrix_norm):
    return {
        'components': model.n_components,
        'relative_reconstruction_error': float(model.reconstruction_err_ / matrix_norm),
        'iterations': int(model.n_iter_),
        'warnings': messages,
        'top_terms': [', '.join(terms[component.argsort()[-8:][::-1]])
                      for component in model.components_],
    }


def main():
    verify_data(ROOT)
    model_dir = ROOT / 'data/model'
    matrix = load_npz(model_dir / 'tfidf.npz').tocsr()
    review_ids = pd.read_csv(model_dir / 'review_ids.csv', dtype={'review_id': str})
    terms = np.array(json.loads((model_dir / 'vocabulary.json').read_text(encoding='utf-8')))
    if matrix.shape != (len(review_ids), len(terms)):
        raise ValueError('The matrix, row IDs, and vocabulary do not align.')
    if not review_ids.review_id.is_unique or not np.isfinite(matrix.data).all():
        raise ValueError('The model inputs contain duplicate IDs or non-finite weights.')
    matrix_norm = float(np.sqrt(matrix.multiply(matrix).sum()))
    if matrix_norm == 0 or (matrix.data < 0).any():
        raise ValueError('NMF needs a nonzero, nonnegative matrix.')

    print(f'Verified {matrix.shape[0]:,} model rows and {matrix.shape[1]:,} features.', flush=True)
    with threadpool_limits(limits=2):
        reference, reference_weights, messages = fit_model(matrix, 8, 42)
        reference_labels = scale_adjusted_weights(
            reference_weights, reference.components_).argmax(axis=1)
        reference_description = describe_fit(reference, terms, messages, matrix_norm)
        stability = []
        for seed in (7, 19):
            alternative, weights, messages = fit_model(matrix, 8, seed)
            # Match each reference component to one alternative component only.
            similarities = cosine_similarity(reference.components_, alternative.components_)
            left, right = linear_sum_assignment(-similarities)
            labels = scale_adjusted_weights(weights, alternative.components_).argmax(axis=1)
            stability.append({
                'seed': seed,
                'matched_cosine_mean': float(similarities[left, right].mean()),
                'matched_cosine_min': float(similarities[left, right].min()),
                'adjusted_rand_index': float(adjusted_rand_score(reference_labels, labels)),
                'iterations': int(alternative.n_iter_),
                'warnings': messages,
                'matched_topics': [
                    {'topic_id': f'T{a + 1}', 'alternative_topic_id': f'T{b + 1}',
                     'cosine': float(similarities[a, b])}
                    for a, b in zip(left, right)
                ],
            })
        sensitivity = []
        for components in (6, 8, 10):
            if components == 8:
                sensitivity.append(reference_description)
            else:
                model, _, messages = fit_model(matrix, components, 42)
                sensitivity.append(describe_fit(model, terms, messages, matrix_norm))

    result = {
        'method': 'TF-IDF + NMF',
        'purpose': 'Numerical stability checks; not semantic accuracy or complaint prevalence.',
        'input': 'data/model/tfidf.npz',
        'matrix_shape': list(matrix.shape),
        'configuration': {'reference_components': 8, 'reference_seed': 42,
                          'initialization': 'random', 'max_iter': 600,
                          'tolerance': 0.0001, 'thread_limit': 2},
        'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                        'scipy': scipy.__version__, 'scikit_learn': sklearn.__version__},
        'reference': reference_description,
        'stability': stability,
        'sensitivity': sensitivity,
    }
    output = ROOT / 'reports/model_checks.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Saved reports/model_checks.json (reference, two seeds, and three group counts).')


if __name__ == '__main__':
    main()

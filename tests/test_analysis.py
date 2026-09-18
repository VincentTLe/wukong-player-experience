"""Check the public snapshot and the calculations behind the main conclusions."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd
from scipy.sparse import load_npz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from wukong_research.analysis import (
    LENGTH_BANDS, load_reviews, match_rates, scale_adjusted_weights, verify_data,
)


class PublishedDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reviews = load_reviews(ROOT)
        cls.provenance = json.loads((ROOT / 'data/provenance.json').read_text(encoding='utf-8'))

    def test_every_published_input_has_a_matching_checksum(self):
        manifest = json.loads((ROOT / 'data/checksums.json').read_text(encoding='utf-8'))
        required = {'data/review_features.csv', 'data/evidence.csv', 'data/provenance.json',
                    'data/pilot_evaluation.json', 'data/model/tfidf.npz',
                    'data/model/review_ids.csv', 'data/model/vocabulary.json',
                    'data/model/metadata.json', 'data/model/topic_reference.json',
                    'data/model/topic_names.json'}
        self.assertTrue(required.issubset(manifest))
        self.assertEqual(verify_data(ROOT), len(manifest))

    def test_changed_input_is_rejected(self):
        # A checksum check must fail when the bytes change, not just return a count.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            expected = hashlib.sha256(b'original').hexdigest()
            (root / 'data/checksums.json').write_text(
                json.dumps({'data/example.csv': expected}), encoding='utf-8')
            (root / 'data/example.csv').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'Input checksum mismatch'):
                verify_data(root)

    def test_review_ids_dates_and_counts_match_the_collection_contract(self):
        reviews = self.reviews
        start = pd.Timestamp(self.provenance['window_start_utc'])
        end = pd.Timestamp(self.provenance['window_end_exclusive_utc'])
        self.assertEqual(str(reviews.created_utc.dt.tz), 'UTC')
        self.assertEqual((end - start).days, 365)
        self.assertTrue(reviews.created_utc.ge(start).all())
        self.assertTrue(reviews.created_utc.lt(end).all())
        self.assertTrue(reviews.review_id.is_unique)
        self.assertFalse(reviews.review_id.isna().any())
        self.assertEqual(len(reviews), 8200)
        self.assertEqual(int(reviews.recommended.sum()), 7408)
        self.assertEqual(int(reviews.keyword_match.sum()), 1514)
        reconciliation = self.provenance['reconciliation']
        self.assertEqual(reconciliation['included_rows'], len(reviews))
        self.assertEqual(reconciliation['raw_rows'],
                         len(reviews) + reconciliation['before_window']
                         + reconciliation['at_or_after_end'] + reconciliation['duplicate_excess'])

    def test_retrieval_flags_and_all_group_denominators_reconcile(self):
        reviews = self.reviews
        expected_flags = reviews[['story_match', 'world_match', 'emotion_match']].any(axis=1)
        np.testing.assert_array_equal(reviews.keyword_match, expected_flags)
        for grouping in ['recommendation', 'length_band', ['length_band', 'recommendation']]:
            counts = match_rates(reviews, grouping)
            self.assertEqual(int(counts.reviews.sum()), len(reviews))
            self.assertEqual(int(counts.matches.sum()), int(reviews.keyword_match.sum()))
            self.assertTrue(counts.matches.le(counts.reviews).all())
            np.testing.assert_allclose(counts.match_rate, counts.matches / counts.reviews)

    def test_aggregate_reversal_and_shared_length_mix(self):
        overall = match_rates(self.reviews, 'recommendation')
        by_length = match_rates(self.reviews, ['length_band', 'recommendation'])
        rates = by_length.match_rate.unstack('recommendation').reindex(LENGTH_BANDS)
        self.assertGreater(overall.loc['Not recommended', 'match_rate'],
                           overall.loc['Recommended', 'match_rate'])
        self.assertTrue(rates['Recommended'].gt(rates['Not recommended']).all())
        # The common weights must retain all review IDs, including short reviews.
        weights = self.reviews.length_band.value_counts(normalize=True).reindex(LENGTH_BANDS)
        self.assertAlmostEqual(float(weights.sum()), 1.0)
        standardized = rates.mul(weights, axis=0).sum()
        self.assertGreater(standardized['Recommended'], standardized['Not recommended'])
        self.assertAlmostEqual(standardized['Not recommended'], 0.140, delta=0.001)
        self.assertAlmostEqual(standardized['Recommended'], 0.194, delta=0.001)

    def test_sparse_matrix_has_documented_rows_and_vocabulary(self):
        model_dir = ROOT / 'data/model'
        matrix = load_npz(model_dir / 'tfidf.npz').tocsr()
        ids = pd.read_csv(model_dir / 'review_ids.csv', dtype={'review_id': str}).review_id
        vocabulary = json.loads((model_dir / 'vocabulary.json').read_text(encoding='utf-8'))
        metadata = json.loads((model_dir / 'metadata.json').read_text(encoding='utf-8'))
        self.assertEqual(matrix.shape, (len(ids), len(vocabulary)))
        self.assertEqual(matrix.shape, (metadata['fitted_unique_texts'], metadata['vocabulary_size']))
        self.assertTrue(ids.is_unique)
        self.assertEqual(len(vocabulary), len(set(vocabulary)))
        self.assertTrue(np.isfinite(matrix.data).all())
        self.assertTrue((matrix.data >= 0).all())
        self.assertTrue((matrix.getnnz(axis=1) >= metadata['min_distinct_features']).all())
        # The saved row IDs must be an ordered subset of the chronological feature table.
        selected = self.reviews.loc[self.reviews.review_id.isin(ids), 'review_id']
        self.assertEqual(ids.tolist(), selected.tolist())
        np.testing.assert_allclose(np.asarray(matrix.multiply(matrix).sum(axis=1)).ravel(),
                                   1.0, atol=1e-10)

    def test_evidence_preserves_balanced_sampling_and_assistant_authorship(self):
        evidence = pd.read_csv(ROOT / 'data/evidence.csv', dtype={'review_id': str},
                               keep_default_na=False)
        self.assertEqual(len(evidence), 24)
        self.assertTrue(evidence.review_id.is_unique)
        self.assertTrue(evidence.reading_id.is_unique)
        self.assertTrue(evidence.review_id.isin(self.reviews.review_id).all())
        self.assertEqual(evidence.recommendation.value_counts().to_dict(),
                         {'Not recommended': 12, 'Recommended': 12})
        self.assertTrue(evidence.annotator.eq('assistant').all())
        self.assertFalse(evidence.independent_review.any())
        self.assertTrue(evidence.evidence.str.split().str.len().between(1, 25).all())
        self.assertTrue(evidence.review_url.str.startswith('https://steamcommunity.com/').all())
        self.assertTrue(evidence.interpretation.str.strip().ne('').all())
        self.assertNotIn('review', evidence.columns)  # Only short excerpts are distributed.

    def test_pilot_evaluation_counts_keep_unclear_cases_visible(self):
        pilot = json.loads((ROOT / 'data/pilot_evaluation.json').read_text(encoding='utf-8'))
        self.assertEqual(pilot['true_positives'] + pilot['false_positives']
                         + pilot['unclear_matching'], pilot['matching_sample'])
        self.assertEqual(pilot['false_negatives'] + pilot['true_negatives'],
                         pilot['nonmatching_sample'])
        self.assertEqual(pilot['matching_sample'] + pilot['nonmatching_sample'], 40)
        self.assertEqual(pilot['annotation_source'], 'assistant')
        self.assertFalse(pilot['independent_human_validation'])


class FactorScaleTests(unittest.TestCase):
    def test_component_rescaling_cannot_change_normalized_weights(self):
        weights = np.array([[2., 1.], [1., 3.]])
        components = np.array([[1., 2., 3.], [3., 2., 1.]])
        scale = np.array([10., 0.1])
        expected = scale_adjusted_weights(weights, components)
        actual = scale_adjusted_weights(weights / scale, components * scale[:, None])
        np.testing.assert_allclose(actual, expected)
        np.testing.assert_allclose(actual.sum(axis=1), 1.0)

    def test_empty_weights_remain_zero_and_finite(self):
        actual = scale_adjusted_weights(np.zeros((2, 3)), np.ones((3, 4)))
        np.testing.assert_array_equal(actual, np.zeros((2, 3)))
        self.assertTrue(np.isfinite(actual).all())


if __name__ == '__main__':
    unittest.main()

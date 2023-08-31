from syndiffix.counters import *

SALT = bytes([])
NOISELESS_SUPPRESSION = SuppressionParams()
NOISELESS_SUPPRESSION.layer_sd = 0.0
NOISELESS_PARAMS = AnonymizationParams()
NOISELESS_PARAMS.low_count_params = NOISELESS_SUPPRESSION
NOISELESS_PARAMS.layer_noise_sd = 0.0
NOISELESS_PARAMS.outlier_count.upper = NOISELESS_PARAMS.outlier_count.lower
NOISELESS_PARAMS.top_count.upper = NOISELESS_PARAMS.top_count.lower
NOISELESS_CONTEXT = AnonymizationContext(bucket_seed=np.uint64(123), anonymization_params=NOISELESS_PARAMS)


def test_unique_aid_low_count() -> None:
    counter = UniqueAidCountersFactory().create_entity_counter()
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    counter.add((np.uint64(1),))
    counter.add((np.uint64(2),))
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    counter.add((np.uint64(3),))
    assert not counter.is_low_count(SALT, NOISELESS_SUPPRESSION)


def test_unique_aid_noisy_count() -> None:
    counter = UniqueAidCountersFactory().create_row_counter()
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(1),))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 1
    counter.add((np.uint64(2),))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 2


def test_generic_aid_low_count() -> None:
    counter = GenericAidCountersFactory(1, 100).create_entity_counter()
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    counter.add((np.uint64(1),))
    counter.add((np.uint64(2),))
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    # Duplicates - no impact.
    counter.add((np.uint64(2),))
    counter.add((np.uint64(2),))
    counter.add((np.uint64(2),))
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    # Null AID - no impact.
    counter.add((np.uint64(0),))
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    counter.add((np.uint64(3),))
    assert not counter.is_low_count(SALT, NOISELESS_SUPPRESSION)


def test_generic_aid_noisy_count() -> None:
    counter = GenericAidCountersFactory(1, 100).create_row_counter()
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(1),))
    counter.add((np.uint64(2),))
    # Flattening not possible.
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(3),))
    counter.add((np.uint64(4),))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 4
    counter.add((np.uint64(4),))
    counter.add((np.uint64(4),))
    # Flattening.
    assert counter.noisy_count(NOISELESS_CONTEXT) == 4
    counter.add((np.uint64(2),))
    counter.add((np.uint64(3),))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 6
    # Null AID - becomes flattened unaccounted for.
    counter.add((np.uint64(0),))
    counter.add((np.uint64(0),))
    counter.add((np.uint64(0),))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 7


def test_multi_aid_low_count() -> None:
    counter = GenericAidCountersFactory(2, 100).create_entity_counter()
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    counter.add((np.uint64(1), np.uint64(1)))
    counter.add((np.uint64(2), np.uint64(2)))
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    # Duplicates - no impact.
    counter.add((np.uint64(2), np.uint64(1)))
    counter.add((np.uint64(1), np.uint64(2)))
    counter.add((np.uint64(1), np.uint64(1)))
    counter.add((np.uint64(2), np.uint64(2)))
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    # Null AID - no impact.
    counter.add((np.uint64(0), np.uint64(0)))
    counter.add((np.uint64(1), np.uint64(0)))
    counter.add((np.uint64(0), np.uint64(1)))
    assert counter.is_low_count(SALT, NOISELESS_SUPPRESSION)
    counter.add((np.uint64(3), np.uint64(3)))
    assert not counter.is_low_count(SALT, NOISELESS_SUPPRESSION)


def test_multi_aid_noisy_count_identical() -> None:
    # Both AIDs are identical - a simple sanity test.
    counter = GenericAidCountersFactory(2, 100).create_row_counter()
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(1), np.uint64(1)))
    counter.add((np.uint64(2), np.uint64(2)))
    # Flattening not possible.
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(3), np.uint64(3)))
    counter.add((np.uint64(4), np.uint64(4)))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 4
    counter.add((np.uint64(4), np.uint64(4)))
    counter.add((np.uint64(4), np.uint64(4)))
    # Flattening.
    assert counter.noisy_count(NOISELESS_CONTEXT) == 4
    counter.add((np.uint64(2), np.uint64(2)))
    counter.add((np.uint64(3), np.uint64(3)))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 6
    # Null AID - becomes flattened unaccounted for.
    counter.add((np.uint64(0), np.uint64(0)))
    counter.add((np.uint64(0), np.uint64(5)))
    counter.add((np.uint64(6), np.uint64(0)))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 7


def test_multi_aid_noisy_count_divergent() -> None:
    counter = GenericAidCountersFactory(2, 100).create_row_counter()
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(1), np.uint64(1)))
    counter.add((np.uint64(2), np.uint64(2)))
    counter.add((np.uint64(2), np.uint64(1)))
    counter.add((np.uint64(1), np.uint64(2)))
    # Flattening not possible in both AIDs.
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(3), np.uint64(3)))
    counter.add((np.uint64(3), np.uint64(4)))
    # Flattening not possible in first AID.
    assert counter.noisy_count(NOISELESS_CONTEXT) == 0
    counter.add((np.uint64(4), np.uint64(3)))
    counter.add((np.uint64(4), np.uint64(4)))
    assert counter.noisy_count(NOISELESS_CONTEXT) == 8
    counter.add((np.uint64(4), np.uint64(4)))
    counter.add((np.uint64(4), np.uint64(4)))
    # Flattening.
    assert counter.noisy_count(NOISELESS_CONTEXT) == 8
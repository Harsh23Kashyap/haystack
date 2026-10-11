# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

import pytest

from haystack.document_stores.types import FilterPolicy, apply_filter_policy


def test_merge_two_comparison_filters():
    """
    Merging two comparison filters

    Result: AND operator with both filters
    """
    init_filters = {"field": "meta.date", "operator": ">=", "value": "2015-01-01"}
    runtime_filters = {"field": "meta.type", "operator": "==", "value": "article"}
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.date", "operator": ">=", "value": "2015-01-01"},
            {"field": "meta.type", "operator": "==", "value": "article"},
        ],
    }


def test_merge_init_comparison_and_runtime_logical_filters():
    """
    Merging init comparison and runtime logical filters

    Result: AND operator with both filters
    """
    init_filters = {"field": "meta.date", "operator": ">=", "value": "2015-01-01"}
    runtime_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
        ],
    }
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
            {"field": "meta.date", "operator": ">=", "value": "2015-01-01"},
        ],
    }


def test_merge_runtime_comparison_and_init_logical_filters_with_string_operators():
    """
    Merging a runtime comparison filter with an init logical filter, but with string-based logical operators

    Result: AND operator with both filters
    """
    # Test with string-based logical operators
    init_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
        ],
    }
    runtime_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.genre", "operator": "IN", "value": ["economy", "politics"]},
            {"field": "meta.publisher", "operator": "==", "value": "nytimes"},
        ],
    }
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
            {"field": "meta.genre", "operator": "IN", "value": ["economy", "politics"]},
            {"field": "meta.publisher", "operator": "==", "value": "nytimes"},
        ],
    }


def test_merge_runtime_comparison_and_init_logical_filters():
    """
    Merging a runtime comparison filter with an init logical filter

    Result: AND operator with both filters
    """
    init_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
        ],
    }
    runtime_filters = {"field": "meta.date", "operator": ">=", "value": "2015-01-01"}
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
            {"field": "meta.date", "operator": ">=", "value": "2015-01-01"},
        ],
    }


def test_merge_two_logical_filters():
    """
    Merging two logical filters

    Result: AND operator with both filters
    """
    init_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
        ],
    }
    runtime_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.genre", "operator": "IN", "value": ["economy", "politics"]},
            {"field": "meta.publisher", "operator": "==", "value": "nytimes"},
        ],
    }
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.rating", "operator": ">=", "value": 3},
            {"field": "meta.genre", "operator": "IN", "value": ["economy", "politics"]},
            {"field": "meta.publisher", "operator": "==", "value": "nytimes"},
        ],
    }


def test_merge_with_different_logical_operators():
    """
    Merging with a different logical operator

    Result: warnings and runtime filters
    """
    init_filters = {"operator": "AND", "conditions": [{"field": "meta.type", "operator": "==", "value": "article"}]}
    runtime_filters = {
        "operator": "OR",
        "conditions": [{"field": "meta.genre", "operator": "IN", "value": ["economy", "politics"]}],
    }
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == runtime_filters


def test_merge_comparison_filters_with_same_field():
    """
    Merging comparison filters with the same field

    Result: warnings and runtime filters
    """
    init_filters = {"field": "meta.date", "operator": ">=", "value": "2015-01-01"}
    runtime_filters = {"field": "meta.date", "operator": "<=", "value": "2020-12-31"}
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == runtime_filters


@pytest.mark.parametrize("logical_operator", ["AND", "OR", "NOT"])
def test_merge_with_custom_logical_operator(logical_operator: Literal["AND", "OR", "NOT"]) -> None:
    """
    Merging with a custom logical operator

    Result: The given logical operator with both filters
    """
    init_filters = {"field": "meta.date", "operator": ">=", "value": "2015-01-01"}
    runtime_filters = {"field": "meta.type", "operator": "==", "value": "article"}
    result = apply_filter_policy(
        FilterPolicy.MERGE, init_filters, runtime_filters, default_logical_operator=logical_operator
    )
    assert result == {
        "operator": logical_operator,
        "conditions": [
            {"field": "meta.date", "operator": ">=", "value": "2015-01-01"},
            {"field": "meta.type", "operator": "==", "value": "article"},
        ],
    }


def test_merge_two_logical_filters_and_dedups_overlapping_field():
    """
    AND+AND merge with overlapping field on comparison conditions.

    Pre-fix, ``combine_two_logical_filters`` simply concatenated the conditions, producing
    ``AND[meta.lang == 'en', meta.lang == 'de']`` — an empty intersection that silently
    returned no documents. The runtime value now overwrites the init value on the same
    field, matching the docstring contract of ``FilterPolicy.MERGE`` ("values from the
    runtime filters will overwrite those from the initial filters") and the behavior of
    the other three shape combinations.
    """
    init_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.lang", "operator": "==", "value": "en"},
            {"field": "meta.type", "operator": "==", "value": "article"},
        ],
    }
    runtime_filters = {"operator": "AND", "conditions": [{"field": "meta.lang", "operator": "==", "value": "de"}]}
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.lang", "operator": "==", "value": "de"},
            {"field": "meta.type", "operator": "==", "value": "article"},
        ],
    }


def test_merge_two_logical_filters_and_keeps_disjoint_fields():
    """
    AND+AND merge with disjoint fields concatenates the conditions.

    Locks the dedup loop: a runtime condition whose field is NOT in the init conditions is
    appended as-is. The non-overlap case must continue to work — the fix only changes the
    overlap case.
    """
    init_filters = {"operator": "AND", "conditions": [{"field": "meta.type", "operator": "==", "value": "article"}]}
    runtime_filters = {"operator": "AND", "conditions": [{"field": "meta.genre", "operator": "==", "value": "economy"}]}
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"field": "meta.genre", "operator": "==", "value": "economy"},
        ],
    }


def test_merge_two_logical_filters_and_keeps_nested_logical():
    """
    AND+AND merge with a nested logical runtime condition appends without dedup.

    Nested logical conditions have no ``field`` key, so the dedup loop appends them as-is.
    A nested logical init condition is also untouched.
    """
    init_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "article"},
            {"operator": "OR", "conditions": [{"field": "meta.rating", "operator": ">=", "value": 4}]},
        ],
    }
    runtime_filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "blog"},
            {"operator": "OR", "conditions": [{"field": "meta.genre", "operator": "==", "value": "tech"}]},
        ],
    }
    result = apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert result == {
        "operator": "AND",
        "conditions": [
            {"field": "meta.type", "operator": "==", "value": "blog"},
            {"operator": "OR", "conditions": [{"field": "meta.rating", "operator": ">=", "value": 4}]},
            {"operator": "OR", "conditions": [{"field": "meta.genre", "operator": "==", "value": "tech"}]},
        ],
    }


def test_merge_two_logical_filters_and_overlap_warns(caplog):
    """
    AND+AND merge with overlapping field logs a warning naming the init and runtime conditions.

    Matches the behavior of the other three shape combinations (``combine_two_comparison_filters``
    and the two ``combine_*_comparison_and_*_logical_filters`` functions) which all log a warning
    when an init filter is overridden by a runtime filter on the same field.
    """
    import logging

    init_filters = {"operator": "AND", "conditions": [{"field": "meta.lang", "operator": "==", "value": "en"}]}
    runtime_filters = {"operator": "AND", "conditions": [{"field": "meta.lang", "operator": "==", "value": "de"}]}
    with caplog.at_level(logging.WARNING, logger="haystack.document_stores.types.filter_policy"):
        apply_filter_policy(FilterPolicy.MERGE, init_filters, runtime_filters)
    assert "is ignored as the field is already present" in caplog.text

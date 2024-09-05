"""
Break crawler-user-agents.json in ways that validate.py should detect

Usage:
$ pytest test_validation.py

"""

import json
import subprocess
from typing import Iterator

from crawleruseragents import UserAgent
import pytest


def update_json_file(data: list[UserAgent]) -> None:
    with open("crawler-user-agents.json", "w") as f:
        json.dump(data, f, indent=2)


@pytest.fixture
def restore_original_json() -> Iterator[None]:
    # Load original version of crawler-user-agents.json
    with open("crawler-user-agents.json") as f:
        original_json = json.load(f)

    # By using a yield statement instead of return, all the code after
    # the yield statement serves as the teardown code:
    yield None

    # tear down code: restore original version of crawler-user-agents.json
    update_json_file(original_json)


def assert_validate_failed() -> None:
    assert subprocess.call(["python", "validate.py"]) != 0


def assert_validate_passed() -> None:
    assert subprocess.call(["python", "validate.py"]) == 0


def test_simple_pass() -> None:
    # the json must be an array of objects containing "pattern"
    # there must be more than 10 instances to pass
    user_agent_list: list[UserAgent] = [
        {
            "pattern": "foo",
            "instances": [
                "foo",
                "afoo",
                "foob",
                "cfood",
                "/foo/",
                "\\foo\\",
                ":foo:",
                "foo.",
                "!foo",
                "/foo",
                "foo\\",
                "FoofooFoo",
                "foot",
            ],
        }
    ]
    update_json_file(user_agent_list)
    assert_validate_passed()


def test_simplest_pass() -> None:
    # the simplest crawler file passes
    user_agent_list: list[UserAgent] = [{"pattern": "foo", "instances": []}]
    update_json_file(user_agent_list)
    assert_validate_passed()


def test_schema_violation_dict1() -> None:
    # contract: the json must be an array
    user_agent_list: list[UserAgent] = {"foo": None}  # type: ignore
    update_json_file(user_agent_list)
    assert_validate_failed()


def test_schema_violation_dict2() -> None:
    # contract: the json must be an array of objects containing "pattern"
    user_agent_list: list[UserAgent] = [{"foo": None}]  # type: ignore
    update_json_file(user_agent_list)
    assert_validate_failed()


def test_schema_violation_dict3() -> None:
    # contract: the json must be an array of objects containing "pattern" and valid properties
    user_agent_list: list[UserAgent] = [
        {"pattern": "foo", "foo": 3}  # type: ignore
    ]
    update_json_file(user_agent_list)
    assert_validate_failed()


def test_simple_duplicate_detection() -> None:
    # contract: if we have the same pattern twice, it fails
    user_agent_list: list[UserAgent] = [
        {
            "instances": [
                "foo",
                "afoo",
                "foob",
                "cfood",
                "/foo/",
                "\\foo\\",
                ":foO:",
                "foo.",
                "!foo",
                "/foo",
                "foo\\",
                "FoofooFoo",
                "foot",
            ],
            "pattern": "foo",
        },
        {
            "instances": [],
            "pattern": "foo",
        },
    ]
    update_json_file(user_agent_list)
    assert_validate_failed()


def test_simple_duplicate_detection2() -> None:
    # contract: if we have the same pattern twice, it fails (even w/o instances)
    user_agent_list: list[UserAgent] = [
        {
            "instances": [
                "foo",
                "afoo",
                "foob",
                "cfood",
                "/foo/",
                "\\foo\\",
                ":foo:",
                "foo.",
                "!foo",
                "/foo",
                "foo\\",
                "FoofooFoo",
                "foot",
            ],
            "pattern": "foo",
        },
        {"instances": [], "pattern": "bar"},
        {"instances": [], "pattern": "bar"},
    ]
    update_json_file(user_agent_list)
    assert_validate_failed()


def test_subset_duplicate_detection() -> None:
    # contract: if a pattern matches another pattern, it fails
    user_agent_list: list[UserAgent] = [
        {
            "instances": [
                "foo",
                "afoo",
                "foob",
                "cfood",
                "/foo/",
                "\\foo\\",
                ":foo:",
                "foo.",
                "!foo",
                "/foo",
                "foo\\",
                "FoofooFoo",
                "foot",
            ],
            "pattern": "foo",
        },
        {"instances": [], "pattern": "afoot"},
    ]
    update_json_file(user_agent_list)
    assert_validate_failed()


def test_case_sensitivity() -> None:
    # contract: the patterns are case sensitive
    user_agent_list: list[UserAgent] = [
        {
            "instances": [
                "FOO",
                "aFoo",
                "foob",
                "cfood",
                "/foo/",
                "\\foo\\",
                ":foo:",
                "fOo.",
                "!FOO",
                "/foo",
                "foo\\",
                "FoofooFoo",
                "foot",
            ],
            "pattern": "foo",
        }
    ]
    update_json_file(user_agent_list)
    assert_validate_failed()


def test_duplicate_case_insensitive_detection() -> None:
    # contract: fail if we have patterns that differ only in capitailization
    user_agent_list: list[UserAgent] = [
        {
            "instances": [
                "foo",
                "afoo",
                "foob",
                "cfood",
                "/foo/",
                "\\foo\\",
                ":foo:",
                "foo.",
                "!foo",
                "/foo",
                "foo\\",
                "FoofooFoo",
                "foot",
            ],
            "pattern": "foo",
        },
        {"instances": [], "pattern": "fOo"},
    ]
    update_json_file(user_agent_list)
    assert_validate_failed()

import pytest
from fastapi import HTTPException, status

from app.common import (
    check_topic_action_tags_integrity,
)


class TestCheckTopicActionTagsIntegrity:
    @property
    def test_func(self):
        return check_topic_action_tags_integrity

    def test_return_true_on_empty_action_tags(self) -> None:
        assert self.test_func([], None)
        assert self.test_func([], [])
        assert self.test_func(["alpha"], [])

    def test_return_true_on_exact_match_tags(self) -> None:
        assert self.test_func(["alpha:bravo:"], ["alpha:bravo:"])  # parent
        assert self.test_func(["alpha:bravo:charlie"], ["alpha:bravo:charlie"])  # child
        assert self.test_func(["alpha"], ["alpha"])  # neither

    def test_return_true_on_match_with_parent(self) -> None:
        assert self.test_func(["alpha:bravo:"], ["alpha:bravo:charlie"])

    def test_return_false_on_mismatch_tags(self) -> None:
        assert not self.test_func(["alpha"], ["bravo"])
        assert not self.test_func(["alpha:bravo:charlie"], ["alpha:bravo:delta"])
        assert not self.test_func(["alpha:bravo:charlie"], ["alpha:bravo:"])

    def test_raise_httpexception_on_error_if_specified(self) -> None:
        with pytest.raises(HTTPException) as error:
            self.test_func([], ["bravo"], on_error=status.HTTP_400_BAD_REQUEST)
        assert error.value.status_code == status.HTTP_400_BAD_REQUEST
        assert error.value.detail == "Action Tag mismatch with Topic Tag"

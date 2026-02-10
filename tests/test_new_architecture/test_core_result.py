import pytest
from app.core.result import Result, Ok, Err, UnwrapError


class TestResult:
    def test_ok_creation(self):
        result = Result.ok(42)
        assert result.is_ok
        assert result.unwrap() == 42
    
    def test_err_creation(self):
        result = Result.err("error")
        assert result.is_err
        assert result.unwrap_err() == "error"
    
    def test_unwrap_on_err_raises(self):
        result = Result.err("fail")
        with pytest.raises(UnwrapError):
            result.unwrap()
    
    def test_unwrap_or_with_default(self):
        assert Result.err("fail").unwrap_or(0) == 0
        assert Result.ok(42).unwrap_or(0) == 42
    
    def test_map_transforms_value(self):
        result = Result.ok(5).map(lambda x: x * 2)
        assert result.unwrap() == 10

from app.utils.common import isnumber


def test_isnumber():
    assert isnumber("12")
    assert isnumber("12.4")
    assert isnumber("-1234")
    assert not isnumber("hello")
    assert not isnumber("what?.asd12")

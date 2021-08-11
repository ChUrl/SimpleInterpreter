from objmodel import W_Integer, W_NormalObject


def test_normalobject():
    w1 = W_NormalObject()
    # 'setvalue' and 'getvalue' write and read the attributes by name.
    w1.setvalue('abc', W_Integer(6))
    w2 = w1.getvalue('abc')
    assert isinstance(w2, W_Integer)
    assert w2.value == 6
    # a missing attribute...
    assert w1.getvalue('bcd') is None


def test_integer():
    w1 = W_Integer(5)
    assert w1.value == 5
    # W_Integer objects cannot have custom attributes,
    # so getvalue() returns None.
    assert w1.getvalue('abc') is None


def test_istrue():
    assert W_Integer(5).istrue() is True
    assert W_Integer(0).istrue() is False
    assert W_Integer(-1).istrue() is True
    # for now, only W_Integer(0) is false; all the other objects are true.
    assert W_NormalObject().istrue() is True


def test_clone():
    w1 = W_NormalObject()
    w1.setvalue('abc', W_Integer(6))
    w2 = w1.clone()
    assert w2.getvalue('abc').value == 6
    w2.setvalue('abc', W_Integer(99))
    assert w2.getvalue('abc').value == 99
    assert w1.getvalue('abc').value == 6  # still the old value

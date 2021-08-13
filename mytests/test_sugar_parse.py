from simpleparser import parse


def test_parsing():
    assert parse("1 + 2") == parse("1 $int_add(2)")
    assert parse("1 + 2 + 3") == parse("1 $int_add(2) $int_add(3)")
    assert parse("1 + 2 * 3") == parse("1 $int_add(2 $int_mul(3))")
    assert parse("1 - 2 - 3") == parse("1 $int_sub(2) $int_sub(3)")
    assert parse("1 + 2 % 3 / 4 - 5 * 6 + 7++") \
           == parse("1 $int_add(2 $int_mod(3) $int_div(4)) $int_sub(5 $int_mul(6)) $int_add(7 $int_inc)")


def test_parsing_parenthesis():
    assert parse("(1 + 2)") == parse("1 $int_add(2)")
    assert parse("1 * (2 + 3)") == parse("1 $int_mul(2 $int_add(3))")

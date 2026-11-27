import sys


def test_a_test_run_loads_no_freedom_ls_module():
    # Every test module is imported during collection, before any test runs,
    # so this covers them all whatever order the tests run in.
    loaded = [
        name
        for name in sys.modules
        if name == "freedom_ls" or name.startswith("freedom_ls.")
    ]

    assert loaded == []

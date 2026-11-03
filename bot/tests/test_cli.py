"""The command-line entry points at least load (nothing else imports the backtest, so CI wouldn't notice)."""


def test_entry_points_import():
    import beach_bot.backtest  # noqa: F401
    import beach_bot.cli  # noqa: F401

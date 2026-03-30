# Contributing

Thanks for taking a look at `d-post`.

The best contributions here are usually the boring ones: a clear bug report, a
small fix, a focused test, or a doc change that makes the next person faster.
This project is easier to maintain when changes stay scoped, readable, and easy
to verify.

## Getting Set Up

Install the project in editable mode with the development tools:

```powershell
python -m pip install -e ".[dev]"
```

If you need to work on the Kadi integration too:

```powershell
python -m pip install -e ".[dev,kadi]"
```

If you want the repo hooks too, install `pre-commit` and enable them:

```powershell
python -m pip install pre-commit
python -m pre_commit install
```

## What To Work On

Good contribution targets:

- core runtime behavior under `src/d_post`
- tests
- docs and examples that help someone get oriented quickly

Try to avoid broad drive-by refactors. A tight change with a clear reason is
much easier to review than a large cleanup mixed with behavior changes.

## Before You Open A Change

Run the usual checks:

```powershell
python -m ruff check .
python -m black .
python -m pytest
```

If your change touches Python code, make sure the tests around that area still
read clearly. If you fix a bug, add or update a test that proves the fix.

## Opening An Issue

When you file a bug or request, include the basics:

- what you expected to happen
- what actually happened
- Windows version
- Python version
- the exact command you ran
- a minimal repro, if you can provide one

That is usually enough to make the next step obvious.

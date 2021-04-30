from dsw_sdk.common.snapshot import (
    Snapshot,
    SnapshotDiff,
    make_snapshot,
    snapshots_diff,
)


class Test:
    def to_json(self):
        return {'foo': 'bar'}


def test_snapshot_diff():
    diff = SnapshotDiff()

    assert bool(diff) is False
    assert len(diff) == 0
    assert 'a' not in diff
    assert 'b' not in diff

    diff.modified = {'a': 123}
    diff.removed = {'b': None}

    assert bool(diff) is True
    assert len(diff) == 2
    assert 'a' in diff
    assert 'b' in diff


def test_make_snapshot():
    snapshot = make_snapshot(Test())
    assert 'foo' in snapshot
    assert snapshot['foo'] == 'bar'


def test_snapshots_diff():
    old_snapshot = Snapshot({'foo': 'bar', 'old': []})
    new_snapshot = Snapshot({'foo': 123, 'bar': 'new'})
    diff = snapshots_diff(old_snapshot, new_snapshot)
    assert diff.modified == {'foo': 'bar'}
    assert diff.removed == {'old': []}
    assert diff.added == {'bar': 'new'}

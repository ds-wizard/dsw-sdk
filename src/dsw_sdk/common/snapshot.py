from typing import Any, Dict

from dsw_sdk.common.attributes import AttributesMixin


class Snapshot:
    def __init__(self, json_repr: Dict[str, Any]):
        self._json_repr = json_repr

    def __contains__(self, item):
        return self._json_repr.__contains__(item)

    def __getitem__(self, item):
        return self._json_repr.__getitem__(item)

    def items(self):
        return self._json_repr.items()


class SnapshotDiff:
    def __init__(self):
        self.modified = {}
        self.added = {}
        self.removed = {}

    def __bool__(self):
        return bool({**self.modified, **self.added, **self.removed})

    def __contains__(self, item):
        return (
            item in self.modified
            or item in self.added
            or item in self.removed
        )

    def __len__(self):
        return len(self.modified) + len(self.added) + len(self.removed)


def make_snapshot(obj: AttributesMixin) -> Snapshot:
    return Snapshot(obj.to_json())


def snapshots_diff(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    snapshot_diff = SnapshotDiff()

    for key, value in old.items():
        if key not in new:
            snapshot_diff.removed[key] = value
        elif value != new[key]:
            snapshot_diff.modified[key] = value

    for key, value in new.items():
        if key not in old:
            snapshot_diff.added[key] = value

    return snapshot_diff

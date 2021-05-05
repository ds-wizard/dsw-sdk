"""
Module containing all classes and functions
responsible for dealing with snapshots.
"""
from __future__ import annotations

from typing import Any, Dict, ItemsView

from dsw_sdk.common.attributes import AttributesMixin


class Snapshot:
    """
    Snapshot of an object's state in a particular point of time.

    For now, it's basically just a dict.
    """

    def __init__(self, json_repr: Dict[str, Any]):
        self._json_repr = json_repr

    def __contains__(self, item):
        return self._json_repr.__contains__(item)

    def __getitem__(self, item):
        return self._json_repr.__getitem__(item)

    def items(self) -> ItemsView[str, Any]:
        """
        Mimics the built-in :meth:`dict.items` method.

        :return: Exactly the same result as a ``dict.items()`` would.
        """
        return self._json_repr.items()


class SnapshotDiff:
    """
    Class representing the differences between two snapshots (instances
    of :class:`Snapshot` class).

    Contains 3 categories:
        - what was modified (same keys, different values)
        - what was added (new keys)
        - what was deleted (old keys not present anymore)
    """

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
    """
    Creates a snapshot from :class:`AttributesMixin` instance.

    :param obj: instance of class :class:`AttributesMixin`

    :return: snapshot of ``obj`` state
    """
    return Snapshot(obj.to_json())


def snapshots_diff(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """
    Compares two snapshots (assuming the first one is older and the
    second one is newer), returning attributes in which they differ.

    :param old: former state of the object
    :param new: newer (current) state of the object

    :return: attributes that was added, changed or deleted
    """
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

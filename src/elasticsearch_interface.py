#! /usr/bin/env python3
"""ElasticsearchProvidesRelation."""
import socket

from ops.framework import (
    EventBase,
    Object,
    ObjectEvents,
)


class ElasticSearchAvailableEvent(EventBase):
    """Available Event."""


class ElasticSearchEvents(ObjectEvents):
    """Interface Events."""


class ElasticSearchInterface(Object):
    """Connect Slurmctld to elasticsearch."""

    def __init(self, charm, relation_name):
        """Set the provide relation data."""
        super().__init__(charm, relation_name)
        self.framework.observe(
            charm.on[self.relation_name].relation_created,
            self._on_relation_created
        )

        def _on_relation_created(self, event):
            """Set data on relation created."""
            event.relation.data[self.model.unit]['hostname'] = socket.gethostname().split(".")[0]

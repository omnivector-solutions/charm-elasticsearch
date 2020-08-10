#! /usr/bin/env python3
"""SlurmdbdProvidesRelation."""
import logging
import socket
from ops.framework import (
    EventBase,
    EventSource,
    Object,
    ObjectEvents,
)   

class ElasticSearchAvailableEvent(EventBase):
    pass

class ElasticSearchEvents(ObjectEvents):
    pass

class ElasticSearchInterface(Object):
    """Connect Slurmctld to elasticsearch"""
    def __init(self, charm, relation_name):
        """set the provide relation data"""
        super().__init__(charm, relation_name)

        self.charm = charm
        self.framework.observe(
            charm.on[self._relation_name].relation_created,
            self._on_relation_created
        )
        def _on_relation_created(self, event):
            event.relation.data[self.model.unit]['hostname'] = socket.gethostname().split(".")[0]

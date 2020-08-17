#!/usr/bin/python3
"""ElasticsearchCharm."""
import logging
import os
from pathlib import Path
import socket
import subprocess

from jinja2 import Environment, FileSystemLoader
from ops.charm import CharmBase
from ops.framework import Object
from ops.main import main
from ops.model import ActiveStatus
from ops.framework import (
    ObjectEvents,
    Object,
    EventSource,
    EventBase,
    StoredState
)

logger = logging.getLogger()


class ElasticsearchProvides(Object):
    """Provide host."""

    def __init__(self, charm, relation_name):
        """Set data on relation created."""
        super().__init__(charm, relation_name)

        self.framework.observe(
            charm.on[relation_name].relation_created,
            self.on_relation_created
        )

    def on_relation_created(self, event):
        """Set host on relation created."""
        event.relation.data[self.model.unit]['host'] = socket.gethostname().split(".")[0]

class NodeAddedEvent(EventBase):
    """Emitted when a node joins the elasticsearch cluster."""

class ElasticEvents(ObjectEvents):
    """Interface events."""
    node_added = EventSource(NodeAddedEvent)

class ElasticCluster(ObjectEvents):
    """Peer relation interface for elasticsearch."""

    on = ElasticEvents()

    def __init__(self, charm, relation_name):
        """Handle relation events."""
        super().__init__(charm, relation_name)

        self.charm = charm
        self.hostname = socket.gethostname()
        event_handler_bindings = {
            charm.on[relation_name].relation_created:
            self._on_relation_created,
            
            charm.on[relation_name].relation_joined:
            self._on_relation_joined,
            
            charm.on[relation_name].relation_changed:
            self._on_relation_changed,
            
            charm.on[relation_name].relation_departed:
            self._on_relation_departed,

            charm.on[relation_name].relation_broken:
            self._on_relation_broken,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    
    def _on_relation_created(self, event):
        logger.debug("################ LOGGING RELATION CREATED ####################")
        #addreses = event.relation.data[self.model.unit]['ingress-address']
        event.relation.data[self.model.unit]['node-name'] = socket.gethostname()

    def _on_relation_joined(self, event):
        logger.debug("################ LOGGING RELATION JOINED ####################")

    def _on_relation_changed(self, event):
        logger.debug("################ LOGGING RELATION CHANGED ####################")
        relations = self.framework.model.relations["elastic-cluster"]
        nodes_info = []
        # this is to add own units info
        nodes_info.append({
            'host': event.relation.data[self.model.unit]['ingress-address'],
            'name': socket.gethostname()
        })
        for relation in relations:
            for unit in relation.units:
                nodes_info.append({
                    'host': relation.data[unit]['ingress-address'],
                    'name': relation.data[unit]['node-name']
                })
        self.charm.stored.elastic_config = nodes_info
        logger.debug(f'hosts: {nodes_info}')
        self.on.node_added.emit()
    
    def _on_relation_departed(self, event):
        logger.debug("################ LOGGING RELATION DEPARTED ####################")

    def _on_relation_broken(self, event):
        logger.debug("################ LOGGING RELATION BROKEN ####################")


class ElasticsearchCharm(CharmBase):
    """Operator charm for Elasticsearch."""

    stored = StoredState()

    def __init__(self, *args):
        """Initialize charm, configure states, and events to observe."""
        super().__init__(*args)
        self.elasticsearch_provies = ElasticsearchProvides(self, "elasticsearch")
        self.elasticsearch_peer = ElasticCluster(self, "elastic-cluster")
        self.stored.set_default(
            elastic_config=None,
        )

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.start: self._on_start,
            self.elasticsearch_peer.on.node_added: self._on_node_added,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        """Install ElasticSearch."""
        subprocess.run(
            ["sudo", "dpkg", "-i", self.model.resources.fetch("elasticsearch")]
        )
        open_port(9200)
        host_name = socket.gethostname()
        ctxt = {"hostname": host_name}
        write_config(ctxt)
        self.unit.status = ActiveStatus("Elasticsearch Installed")

    def _on_start(self, event):
        """Start Elasticseach."""
        subprocess.run(
            ["sudo", "-i", "service", "elasticsearch", "start"])

    def _on_node_added(self, event):
        logger.debug("_on_node_added event going off")
        write_config(
            { 'nodes': self.stored.elastic_config }
        )
        logger.debug(self.stored.elastic_config.__dict__)


def write_config(context):
    """Render the context to a template.

    target: /etc/elasticsearch/elasticsearch.yml
    source: /templates/elasticsearch.yml.tmpl
    file name can also be slurmdbdb.conf
    """
    template_name = "elasticsearch.yml.tmpl"
    template_dir = "templates"
    target = Path("/etc/elasticsearch/elasticsearch.yml")
    rendered_template = Environment(
        loader=FileSystemLoader(template_dir)
    ).get_template(template_name)

    target.write_text(rendered_template.render(context))


def _modify_port(start=None, end=None, protocol='tcp', hook_tool="open-port"):
    assert protocol in {'tcp', 'udp', 'icmp'}
    if protocol == 'icmp':
        start = None
        end = None

    if start and end:
        port = f"{start}-{end}/"
    elif start:
        port = f"{start}/"
    else:
        port = ""
    subprocess.run([hook_tool, f"{port}{protocol}"])


def open_port(start, end=None, protocol="tcp"):
    """Open port in operator charm."""
    _modify_port(start, end, protocol=protocol, hook_tool="open-port")


if __name__ == "__main__":
    main(ElasticsearchCharm)

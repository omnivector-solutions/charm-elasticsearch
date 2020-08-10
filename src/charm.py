#!/usr/bin/python3
"""ElasticsearchCharm."""
import logging
import os
from pathlib import Path
import socket
import subprocess

from elasticsearch_interface import ElasticSearchInterface
from jinja2 import Environment, FileSystemLoader
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger()


class ElasticsearchCharm(CharmBase):
    """Operator charm for Elasticsearch."""

    def __init__(self, *args):
        """Initialize charm, configure states, and events to observe."""
        super().__init__(*args)
        self.elastic_search = ElasticSearchInterface(self, "elasticsearch")
        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.start: self._on_start,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        """Install ElasticSearch."""
        subprocess.run(
            ["sudo", "dpkg", "-i", self.model.resources.fetch("elasticsearch")]
        )
        host_name = socket.gethostname()
        ctxt = {"hostname": host_name}
        write_config(ctxt)
        open_port(9200)
        self.unit.status = ActiveStatus("Elasticsearch Installed")

    def _on_start(self, event):
        """Start Elasticseach."""
        subprocess.run(
            ["sudo", "-i", "service", "elasticsearch", "start"])


def write_config(context):
    """Render the context to a template.

    target: /etc/elasticsearch/elasticsearch.yml
    source: /templates/elasticsearch.yml.tmpl
    file name can also be slurmdbdb.conf
    """
    template_name = "elasticsearch.yml.tmpl"
    template_dir = "templates"
    target = Path("/etc/elasticsearch/elasticsearch.yml")
    logger.info(os.getcwd())
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
    """Open port in operator framework."""
    _modify_port(start, end, protocol=protocol, hook_tool="open-port")


if __name__ == "__main__":
    main(ElasticsearchCharm)

# Elasticsearch Operator Charm
Elasticsearch is a flexible and powerful open source, distributed, real-time search and analytics engine. Architected from the ground up for use in distributed environments where reliability and scalability are must haves, Elasticsearch gives you the ability to move easily beyond simple full-text search. Through its robust set of APIs and query DSLs, plus clients for the most popular programming languages, Elasticsearch delivers on the near limitless promises of search technology.

Excerpt from elasticsearch.org


Build
-----
```bashrc
sudo snap install charmcraft --classic
charmcraft build
```

Deploy
-----
This charm has you supply the deb version of elasticsearch. It can be downloaded from:
https://www.elastic.co/downloads/elasticsearch

```bashrc
juju deploy ./elasticsearch.charm --resource elasticsearch=./path/to/elasticsearch.deb
```

Interfaces
----------
Ability to provide the host over interface elasticsearch to relate to your application

```bashrc
juju relate elasticsearch:elasticsearch your_application:elasticsearch
```

Contact
-------
 - Author: OmniVector Solutions 
 - Bug Tracker: [here](https://github.com/omnivector-solutions/charm-slurmdbd)

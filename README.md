# Elasticsearch Charm

Build
-----
```bashrc
sudo snap install charmcraft --classic
charmcraft build
```

Deploy
-----
```bashrc
juju deploy ./elasticsearch.charm
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

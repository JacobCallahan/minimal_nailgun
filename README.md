# minimal_nailgun
Quick examples for how to get started testing Satellite 6 with nailgun

This repo only serves to provide some examples of how to use nailgun 
when starting your own testing repository.

Topics covered include:
 - Loading nailgun config from a file
 - Creating basic entities
 - Creating entities with another entity requirement
 - Entity methods
 - Handling search results
 - Ignoring read fields

Installation
------------
```pip install -r requirements.txt```

Post-Installation
-----------------
Make a copy of nailgun_config.yaml.example and remove the .example.
Then update the configuration options.

Running Tests
-------------
Tests should be run with pytest while in the repo directory.
```pytest -v```

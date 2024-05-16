
# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


# [1.0.0] - `16.05.2024`

### Added

- Repository Set up
- GET ("/graph/welcome/")
  - A welcome/description message
- GET ("/graph/nodes/")
  - Gets 5 nodes from the graph database
- GET ("/graph/labels-and-counts/")
  - Gets the list of the labels along with their cardinality
- GET ("/graph-subset/{label}/{keyword}")
  - The main query that returns the nodes and relationships per label 
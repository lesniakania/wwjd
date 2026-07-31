# Theme discovery data: license review

This file records the licensing decision for external scenario datasets considered for theme
discovery. External examples are editorial inputs, not moral or theological authorities.

## ETHICS — approved for the discovery pipeline

- Project: https://github.com/hendrycks/ethics
- Dataset download: https://people.eecs.berkeley.edu/~hendrycks/ethics.tar
- License: MIT
- Decision: approved for clustering, adaptation, and redistribution with the copyright and license
  notice retained.
- Usage: only the short `commonsense` training scenarios are sampled. Source record identifiers and
  project provenance are retained in every cluster draft. Raw scenarios are not used in application
  responses.

## Social Chemistry 101 — excluded pending a share-alike decision

- Project: https://github.com/mbforbes/social-chemistry-101
- License: CC BY-SA 4.0
- Sources include confessions, Dear Abby, ROCStories, and Am I the Asshole.
- Decision: not imported. Before using it, the project must decide how attribution and ShareAlike
  apply to distributed adaptations and review the privacy and cultural-bias implications of the
  source material.

## Norm Bank / Delphi — excluded

- Publication: https://www.nature.com/articles/s42256-024-00969-6
- Decision: not imported because it combines multiple upstream datasets and licenses. The authors
  also document demographic and cultural limitations in the underlying moral judgments.

## Moral Stories — excluded pending dataset-license verification

- Project: https://github.com/demelin/moral_stories
- Decision: not imported until the license covering the dataset content, rather than only code, is
  confirmed unambiguously.

---
configs:
- config_name: all
  data_files:
  - split: train
    path: all/*
- config_name: efficiency
  data_files:
  - split: train
    path: efficiency/*
- config_name: interpretability
  data_files:
  - split: train
    path: interpretability/*
- config_name: agent_rl
  data_files:
  - split: train
    path: agent_rl/*
license: mit
size_categories:
- n<1K
pretty_name: DailArXivPaper
task_categories:
- text-generation
tags:
- raw
language:
- en
---

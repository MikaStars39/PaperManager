<h1 align="center">ArxivPaperManager</h1>

<p align="center">
   <a href="https://www.python.org/">
        <img alt="Build" src="https://img.shields.io/badge/python-3.10-g">
    </a>
</p>

**Welcome to ArxivPaperManager!**

A simple tool that can manage paper database with natural language prompts and automatically push to huggingface as dataset.

## Quick Start

First clone the repo:

```shell
git clone https://github.com/MikaStars39/PaperManager.git
```

We suggest using uv as the virtual environment manager, you can run the following command to install the venv with pip:

```shell
uv init
uv venv
uv pip install -r requirements.txt
```

Copy the ```config/base.toml``` and create a new config based on your preference (e.g., ```config/test.toml```). Then run the following command to start the agent ui:

```
uv run main.py --config config/test.toml
```

If need to push to huggingface, please export the HF_TOKEN:
```
export HF_TOKEN="xxxx"
```

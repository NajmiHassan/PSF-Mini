# Mini-PSF: Protein Scaffold Filling Web Tool

A simplified web application inspired by the research paper **"PSF: A Web Application Tool for Protein Scaffold Filling"** ([https://psf.ncat.edu/](https://psf.ncat.edu/)).

## What is this?

When scientists sequence proteins, they often end up with **incomplete sequences** that have gaps called **scaffolds**. The goal of "scaffold filling" is to predict the missing amino acids in those gaps.

This mini-project is a Django web app that takes a protein scaffold with gaps (shown as `-` or `?` or `X`) and predicts the most likely amino acids to fill those gaps based on a statistical model trained on real protein data.

## How is this different from the original paper?

| Original PSF Paper | This Mini-PSF |
|---|---|
| Deep learning (LSTM/Transformer) | k-mer frequency model (statistical) |
| Large training dataset | Small built-in dataset |
| Multiple pre-trained models | One simple model |
| Django deployment | Django Deployment |

The **concept** is the same, fill gaps in protein sequences, but this uses a simpler, explainable algorithm so you can show the professor you understand the underlying problem.

## How it works (the algorithm)

1. We have a small reference dataset of real protein sequences.
2. We build a **k-mer frequency table**, for every 3-letter window in real proteins, we record how often each amino acid appears next to its neighbors.
3. When the user gives a scaffold with gaps, we look at the amino acids around each gap and pick the most likely amino acid to fill it (based on the frequency table).
4. We also return a **confidence score** for each prediction.

This is called a **context-based statistical prediction**, it's the same family of ideas used in the paper, just simplified.

## Tech Stack

- **Backend:** Python 3 + Django 4
- **ML/Logic:** Pure Python with a k-mer frequency model
- **Frontend:** HTML + CSS (no heavy frameworks)
- **Data:** Built-in mini protein dataset (you can extend it)

## Setup

```bash
# 1. Install Django
pip install django

# 2. Run migrations (creates SQLite db for history)
python manage.py migrate

# 3. Start the server
python manage.py runserver

# 4. Open in browser
http://127.0.0.1:8000/
```

## What to show the professor

1. **The web interface** — paste a scaffold, get filled prediction with confidence.
2. **The algorithm code** in `scaffold_filler/predictor.py` — clean, commented.
3. **Example test cases** in `examples.md`.
4. **This README** — explains the link to the original paper.

## File structure

```
psf_mini/
├── manage.py
├── scaffold_app/         # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scaffold_filler/      # The actual app
│   ├── predictor.py      # ← THE CORE ALGORITHM
│   ├── views.py          # Web request handlers
│   ├── urls.py
│   ├── models.py         # Saves prediction history
│   ├── templates/scaffold_filler/
│   │   ├── home.html
│   │   └── result.html
│   └── static/scaffold_filler/
│       └── style.css
├── examples.md           # Sample inputs to try
└── README.md
```

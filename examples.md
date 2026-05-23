# Sample Scaffolds to Test

These are sequences derived from real proteins, with gaps introduced for you to demonstrate the tool. The "Expected" column shows what the model should ideally predict (the original residue), and the "Difficulty" reflects how distinctive the surrounding context is.

## 1. Insulin fragment

**Scaffold:**
```
FVNQHLCGSHLVEALYL-CGERG-FYTPKTGIVE-CCTSICSLYQLENYCN
```

**Original (for reference):**
```
FVNQHLCGSHLVEALYLVCGERGFFYTPKTGIVEQCCTSICSLYQLENYCN
```

| Gap position | Expected | Difficulty |
|---|---|---|
| 18 | V | medium |
| 24 | F | medium |
| 35 | Q | medium |

---

## 2. Ubiquitin fragment

**Scaffold:**
```
MQIFVKTLTGKT-TLEVEPSDT-ENVKAKIQDKE-IPPDQQRLIFAGKQLEDGRTL-DYNIQKESTLHLVLRLRGG
```

**Original:**
```
MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG
```

Expected fills: I, I, G, S

---

## 3. Simple test (small sequence)

**Scaffold:**
```
MKTAY-AKQRQ-SFVKS--SRQLEER
```

**Original (approximately):**
```
MKTAYIAKQRQISFVKSHFSRQLEER
```

Expected fills: I, I, H, F

---

## How to demo to your professor

1. **Open the home page** — show the input form and built-in stats.
2. **Click one of the example buttons** — they fill the form automatically.
3. **Submit** — show the filled sequence, per-gap predictions, confidence bars, and source badges (context vs. fallback).
4. **Click "History"** — show that predictions are saved to the SQLite database via the Django ORM.
5. **Click "About"** — explain the k-mer frequency algorithm and how it relates to the deep-learning approach in the original PSF paper.
6. **Show the code** — `scaffold_filler/predictor.py` is heavily commented for this exact purpose.

## Talking points for the professor

- **Why this is similar to PSF:** Both are Django web apps that take a scaffold input and predict amino acids for the gaps.
- **Why this is simpler:** PSF uses deep learning (LSTM/Transformer); this uses a statistical k-mer frequency model. The simpler model is interpretable — every prediction has a clear, explainable reason.
- **Extending it:** Replace `predictor.py` with a PyTorch model and train it on a larger dataset (e.g., UniProt). The rest of the app stays the same.
- **Stack matches the paper:** Django + Python + a model module = the same architecture as the original PSF.

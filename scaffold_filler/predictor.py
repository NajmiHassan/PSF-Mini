"""
============================================================================
 CORE ALGORITHM: Protein Scaffold Filling using k-mer Frequency Model
============================================================================

WHAT THIS FILE DOES
-------------------
A "scaffold" is an incomplete protein sequence with gaps. For example:
    Real protein: MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ
    Scaffold   : MKTAYIAK-RQ-SFVKSHFS--LEERLGLIEVQ

The job of this module is to predict the amino acids that should fill the
gaps (the '-' characters).

THE INSPIRATION
---------------
This is a simplified version of the approach in:
"PSF: A Web Application Tool for Protein Scaffold Filling" (https://psf.ncat.edu/)
The original uses deep learning. We use a much simpler statistical model
so the code is easy to read and explain. The CONCEPT — using the sequence
context around a gap to predict what fits — is the same.

THE ALGORITHM IN 3 STEPS
------------------------
1. TRAINING: We scan through a reference dataset of real proteins. For
   every position, we look at the amino acids on its left and right (the
   "context") and remember which amino acid actually appeared in the
   middle. We store these counts in a frequency table.

2. PREDICTION: When we see a gap in the user's scaffold, we look at the
   amino acids surrounding the gap (the context). We check our frequency
   table to find the amino acid that appears most often in that context.

3. CONFIDENCE: We compute confidence as the proportion of times the
   chosen amino acid appeared in this context, divided by the total
   number of observations for that context.

This is essentially a k-mer language model — a building block of the
deep-learning models used in the real paper.
"""

from collections import defaultdict, Counter

# The 20 standard amino acids (single-letter codes).
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

# Characters the user might use to indicate a gap.
GAP_CHARS = {'-', '?', 'X', 'x', '_', '.'}

# How many amino acids of context to look at on EACH side of a gap.
# A larger window = more specific predictions, but needs more training data.
CONTEXT_SIZE = 2


# ---------------------------------------------------------------------------
# 1. A tiny built-in "reference dataset" of real protein sequences.
#    In a real project, this would come from UniProt or a similar database.
#    For the demo, we include a handful of well-known proteins so you can
#    run it offline without downloading anything.
# ---------------------------------------------------------------------------
REFERENCE_PROTEINS = [
    # Human insulin (mature B-chain + A-chain)
    "FVNQHLCGSHLVEALYLVCGERGFFYTPKTGIVEQCCTSICSLYQLENYCN",
    # Human hemoglobin alpha chain
    "VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKV"
    "ADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHAS"
    "LDKFLASVSTVLTSKYR",
    # Human hemoglobin beta chain
    "VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKA"
    "HGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTP"
    "PVQAAYQKVVAGVANALAHKYH",
    # Lysozyme (chicken)
    "KVFGRCELAAAMKRHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGILQINSRW"
    "WCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWRNRCKGTDVQAWI"
    "RGCRL",
    # Myoglobin (sperm whale)
    "VLSEGEWQLVLHVWAKVEADVAGHGQDILIRLFKSHPETLEKFDRFKHLKTEAEMKASEDLK"
    "KHGVTVLTALGAILKKKGHHEAELKPLAQSHATKHKIPIKYLEFISEAIIHVLHSRHPGDFG"
    "ADAQGAMNKALELFRKDIAAKYKELGYQG",
    # Ubiquitin
    "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQ"
    "KESTLHLVLRLRGG",
    # Cytochrome c (human)
    "MGDVEKGKKIFIMKCSQCHTVEKGGKHKTGPNLHGLFGRKTGQAPGYSYTAANKNKGIIWGE"
    "DTLMEYLENPKKYIPGTKMIFVGIKKKEERADLIAYLKKATNE",
    # Green fluorescent protein (GFP) core
    "MASKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLV"
    "TTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRI"
    "ELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEEDGSVQLADHYQQ"
    "NTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITLGMDELYK",
]


# ---------------------------------------------------------------------------
# 2. The frequency model.
# ---------------------------------------------------------------------------
class KmerFrequencyModel:
    """Learns: for a given (left_context, right_context), what amino acid
    appears in the middle, and how often?"""

    def __init__(self, context_size: int = CONTEXT_SIZE):
        self.context_size = context_size

        # Maps a tuple (left_context, right_context) -> Counter of middle AAs.
        # Example: ("MK", "AY") -> Counter({'T': 12, 'S': 3, ...})
        self.context_table: dict = defaultdict(Counter)

        # Fallback: overall frequency of each amino acid, used when we
        # have never seen the surrounding context before.
        self.global_freq: Counter = Counter()

    def train(self, sequences):
        """Build the frequency table from a list of protein sequences."""
        k = self.context_size
        for seq in sequences:
            seq = seq.upper().strip()
            # Update global frequency.
            self.global_freq.update(c for c in seq if c in AMINO_ACIDS)

            # Slide a window over the sequence.
            # For each position i (with k AAs on each side), record the
            # middle amino acid given its context.
            for i in range(k, len(seq) - k):
                middle = seq[i]
                if middle not in AMINO_ACIDS:
                    continue
                left = seq[i - k:i]
                right = seq[i + 1:i + 1 + k]
                # Skip if the context itself has gaps or unknowns.
                if not (all(c in AMINO_ACIDS for c in left)
                        and all(c in AMINO_ACIDS for c in right)):
                    continue
                self.context_table[(left, right)][middle] += 1

    def predict(self, left: str, right: str):
        """Predict the most likely amino acid given a left + right context.

        Returns a tuple: (predicted_aa, confidence_percent, source)
        - source = 'context' if we used the context table
        - source = 'fallback' if we had to use global frequencies
        """
        counter = self.context_table.get((left, right))

        if counter and sum(counter.values()) > 0:
            total = sum(counter.values())
            top_aa, top_count = counter.most_common(1)[0]
            confidence = (top_count / total) * 100
            return top_aa, round(confidence, 1), 'context'

        # Fallback: use overall amino acid frequencies.
        if self.global_freq:
            total = sum(self.global_freq.values())
            top_aa, top_count = self.global_freq.most_common(1)[0]
            confidence = (top_count / total) * 100
            return top_aa, round(confidence, 1), 'fallback'

        # If the model is empty (shouldn't happen), default to Alanine.
        return 'A', 0.0, 'default'


# ---------------------------------------------------------------------------
# 3. Module-level singleton: train ONCE when the app starts.
# ---------------------------------------------------------------------------
_MODEL = KmerFrequencyModel(context_size=CONTEXT_SIZE)
_MODEL.train(REFERENCE_PROTEINS)


# ---------------------------------------------------------------------------
# 4. The public API used by Django views.
# ---------------------------------------------------------------------------
def fill_scaffold(scaffold: str):
    """Fill all gaps in a scaffold sequence.

    Args:
        scaffold: A string like "MKTAYIAK-RQ-SFVKSHFS--LEERLGLIEVQ".
                  Gaps are any character in GAP_CHARS.

    Returns:
        A dict with:
          - 'original'       : the cleaned input
          - 'filled'         : the predicted full sequence
          - 'predictions'    : list of per-gap details
          - 'gap_count'      : number of gaps that were filled
          - 'avg_confidence' : mean confidence across all predictions
    """
    # Clean input: uppercase, strip whitespace, remove invalid characters.
    cleaned = ''.join(
        c for c in scaffold.upper() if c in AMINO_ACIDS or c in GAP_CHARS
    )

    seq = list(cleaned)
    predictions = []
    k = _MODEL.context_size

    for i, ch in enumerate(seq):
        if ch not in GAP_CHARS:
            continue

        # Extract left context: up to k known AAs immediately before i.
        left = ''
        j = i - 1
        while j >= 0 and len(left) < k:
            if seq[j] in AMINO_ACIDS:
                left = seq[j] + left
            j -= 1

        # Extract right context: up to k known AAs immediately after i.
        right = ''
        j = i + 1
        while j < len(seq) and len(right) < k:
            if seq[j] in AMINO_ACIDS:
                right = right + seq[j]
            j += 1

        # Pad if we don't have enough context.
        left = left.rjust(k, ' ').strip() or ''
        right = right.ljust(k, ' ').strip() or ''

        # Predict.
        if len(left) == k and len(right) == k:
            aa, conf, source = _MODEL.predict(left, right)
        else:
            # Edge of sequence - use fallback.
            aa, conf, source = _MODEL.predict('', '')

        seq[i] = aa
        predictions.append({
            'position': i + 1,        # 1-indexed for display
            'left_context': left,
            'right_context': right,
            'predicted': aa,
            'confidence': conf,
            'source': source,
        })

    filled = ''.join(seq)
    avg_conf = (
        sum(p['confidence'] for p in predictions) / len(predictions)
        if predictions else 0.0
    )

    return {
        'original': cleaned,
        'filled': filled,
        'predictions': predictions,
        'gap_count': len(predictions),
        'avg_confidence': round(avg_conf, 1),
    }


def model_stats():
    """Return basic statistics about the trained model (shown on home page)."""
    total_contexts = len(_MODEL.context_table)
    total_observations = sum(
        sum(c.values()) for c in _MODEL.context_table.values()
    )
    return {
        'reference_protein_count': len(REFERENCE_PROTEINS),
        'total_amino_acids_seen': sum(_MODEL.global_freq.values()),
        'unique_contexts_learned': total_contexts,
        'total_observations': total_observations,
        'context_size': _MODEL.context_size,
    }

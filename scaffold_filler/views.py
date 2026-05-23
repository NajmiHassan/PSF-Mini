"""Views (= web request handlers) for the Mini-PSF app."""
from django.shortcuts import render, redirect
from django.contrib import messages
from .predictor import fill_scaffold, model_stats
from .models import PredictionHistory


def home(request):
    """Landing page with the input form."""
    context = {
        'stats': model_stats(),
        'example_scaffolds': [
            ('Insulin fragment with 3 gaps', 'FVNQHLCGSHLVEALYL-CGERG-FYTPKTGIVE-CCTSICSLYQLENYCN'),
            ('Ubiquitin with 4 gaps',         'MQIFVKTLTGKT-TLEVEPSDT-ENVKAKIQDKE-IPPDQQRLIFAGKQLEDGRTL-DYNIQKESTLHLVLRLRGG'),
            ('Short test sequence',           'MKTAY-AKQRQ-SFVKS--SRQLEER'),
        ],
    }
    return render(request, 'scaffold_filler/home.html', context)


def predict(request):
    """Handle the form submission and run scaffold filling."""
    if request.method != 'POST':
        return redirect('scaffold_filler:home')

    scaffold = request.POST.get('scaffold', '').strip()

    if not scaffold:
        messages.error(request, 'Please enter a scaffold sequence.')
        return redirect('scaffold_filler:home')

    if len(scaffold) > 5000:
        messages.error(request, 'Sequence too long. Please limit to 5000 characters.')
        return redirect('scaffold_filler:home')

    # Run the core algorithm.
    result = fill_scaffold(scaffold)

    if result['gap_count'] == 0:
        messages.warning(
            request,
            'No gaps detected in the sequence. Use "-", "?", or "X" to mark gaps.'
        )

    # Save to database for the history page.
    PredictionHistory.objects.create(
        input_scaffold=result['original'],
        output_filled=result['filled'],
        gap_count=result['gap_count'],
        avg_confidence=result['avg_confidence'],
    )

    return render(request, 'scaffold_filler/result.html', {'result': result})


def history(request):
    """Show the last 20 predictions saved in the database."""
    recent = PredictionHistory.objects.all()[:20]
    return render(request, 'scaffold_filler/history.html', {'records': recent})


def about(request):
    """About page explaining the algorithm and the link to the paper."""
    return render(request, 'scaffold_filler/about.html', {'stats': model_stats()})

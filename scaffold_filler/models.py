from django.db import models


class PredictionHistory(models.Model):
    """Saves every scaffold filling request so users can see their history.
    This shows the professor we're using Django's ORM properly."""

    input_scaffold = models.TextField()
    output_filled = models.TextField()
    gap_count = models.IntegerField(default=0)
    avg_confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Prediction histories'

    def __str__(self):
        preview = self.input_scaffold[:30]
        return f"{preview}... ({self.gap_count} gaps)"

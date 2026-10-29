from django.db import models


class Posting(models.Model):
    # Store the job title and the employer's name.
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)

    # Store the full job description.
    description = models.TextField()

    # Keep the source link so users can review the original posting.
    source_url = models.URLField(max_length=2048)

    # Record when this posting was first saved in our database.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Display a readable label in the admin and Django shell.
        return f"{self.title} at {self.company_name}"
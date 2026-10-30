from rest_framework import serializers

from .models import Posting


class PostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posting
        fields = [
            'id',
            'title',
            'company_name',
            'description',
            'source_url',
            'created_at',
        ]

        read_only_fields = fields
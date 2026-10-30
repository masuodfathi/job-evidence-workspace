from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Posting
from .serializers import PostingSerializer


@api_view(["GET"])
def posting_list(request):
    # Read postings in a consistent order, with the newest first.
    postings = Posting.objects.order_by("-created_at", "-id")

    # Convert multiple model instances into API-friendly data.
    serializer = PostingSerializer(postings, many=True)

    # Return the serialized data as an API response.
    return Response(serializer.data)

@api_view(["GET"])
def posting_detail(request, pk):
    # Retrieve a single posting by its primary key (ID) or return a 404 error if not found.
    posting = get_object_or_404(Posting, pk=pk)

    # Convert the model instance into API-friendly data.
    serializer = PostingSerializer(posting)

    # Return the serialized data as an API response.
    return Response(serializer.data)
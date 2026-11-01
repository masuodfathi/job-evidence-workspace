from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from .models import Posting
from .serializers import PostingSerializer


@api_view(["GET", "POST"])
def posting_list(request):
    if request.method == "POST":

        # Validate the incoming data before saving anything.
        serializer = PostingSerializer(data=request.data)

        # If the data is valid, save it and return the new posting.
        if serializer.is_valid(raise_exception=True):

            # Save the new posting to the database.
            serializer.save()
            
            # Return the newly created posting with a 201 status code.
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
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

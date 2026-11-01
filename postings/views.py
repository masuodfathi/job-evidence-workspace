from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

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
        
    # Define a consistent order before selecting a page.
    postings = Posting.objects.order_by("-created_at", "-id")

    # Read the optional search parameter and remove surrounding whitespace.
    search = request.query_params.get("search", "").strip()

    if search:
        # Filter titles without case sensitivity.
        postings = postings.filter(title__icontains=search)

    # Return at most 20 postings per page.
    paginator = PageNumberPagination()
    paginator.page_size = 20

    # Select this page's records using a database-level limit.
    page = paginator.paginate_queryset(postings, request)

    # Serialize only the records selected for this page.
    serializer = PostingSerializer(page, many=True)

    # Include the total count and navigation links in the response.
    return paginator.get_paginated_response(serializer.data)

@api_view(["GET"])
def posting_detail(request, pk):
    # Retrieve a single posting by its primary key (ID) or return a 404 error if not found.
    posting = get_object_or_404(Posting, pk=pk)

    # Convert the model instance into API-friendly data.
    serializer = PostingSerializer(posting)

    # Return the serialized data as an API response.
    return Response(serializer.data)

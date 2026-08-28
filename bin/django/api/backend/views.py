import io
from .logic import predict
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework.parsers import JSONParser
from .serializers import ReviewDataSerializer
import json
from django.http import JsonResponse


class ReviewDataApiView(APIView):
    def post(self, request: HttpRequest):
        json_data = json.loads(request.body)
        print(json_data)
        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)
        # Create serializer
        serializer = ReviewDataSerializer(data=data)
        print('Got serializer')
        if serializer.is_valid():
            print('Serializer valid')
            # Create object
            request_data = serializer.create(serializer.validated_data)
            # connection to spam model:
            response = predict(request_data)
            return JsonResponse({'result': response})

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

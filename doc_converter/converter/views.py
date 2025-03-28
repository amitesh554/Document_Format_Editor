from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import generics, permissions, status
from django.http import FileResponse
from django.utils.timezone import now
from .models import ConversionRecord
from .serializers import ConversionRecordSerializer
from .utils import convert_file
import os
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view
from django.http import HttpResponse
from PIL import Image
from reportlab.lib.utils import ImageReader

import io


def home(request):
    return render(request,'index.html')

@api_view(['POST'])
def convert(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        
        # Create a PDF response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="converted.pdf"'
        
        pdf = canvas.Canvas(response)
        pdf.drawString(100, 750, f"Converted File: {uploaded_file.name}")
        
        if uploaded_file.content_type.startswith("image"):
            image = Image.open(uploaded_file)
            image = image.convert("RGB")  # Ensure it's in a compatible format
            img_io = io.BytesIO()
            image.save(img_io, format="JPEG")
            img_io.seek(0)
            img_reader = ImageReader(img_io)
            pdf.drawImage(img_reader, 100, 500, width=300, height=300)  # Adjust size as needed


        # # Generate PDF using reportlab
        # pdf = canvas.Canvas(response)
        # pdf.drawString(100, 750, f"Converted File: {uploaded_file.name}")
        # pdf.save()

        return response

    return HttpResponse("Invalid request", status=400)


class ConversionListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ConversionRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get("file")
        target_format = self.request.data.get("converted_format")

        if not uploaded_file or not target_format:
            raise ValueError("File and format must be provided.")

        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

        try:
            with open(file_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # **Convert the file**
            converted_path = convert_file(file_path, target_format)

            # **Ensure file is closed before removing**
            conversion_record = serializer.save(
                user=self.request.user,
                file_name=uploaded_file.name,
                converted_format=target_format,
                upload_date=now(),
            )

            # **Open file in a way that ensures it's fully released before removal**
            with open(converted_path, "rb") as converted_file:
                response = FileResponse(converted_file, as_attachment=True)

            # **Delete files AFTER response is prepared**
            os.remove(file_path)
            os.remove(converted_path)

            return response

        except Exception as e:
            # **Clean up file if any error occurs**
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(converted_path):
                os.remove(converted_path)

            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversionHistoryView(generics.ListAPIView):
    serializer_class = ConversionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ConversionRecord.objects.filter(user=self.request.user)


class ConversionHistoryDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ConversionRecord.objects.all() 
    serializer_class = ConversionRecordSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can delete/update


#This helps admin to view all history of conversion
class AdminConversionHistoryView(generics.ListAPIView):
    queryset = ConversionRecord.objects.all()
    serializer_class = ConversionRecordSerializer
    permission_classes = [permissions.IsAdminUser]

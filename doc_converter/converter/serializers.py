from rest_framework import serializers
from .models import ConversionRecord

class ConversionRecordSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)  # Add this field for file upload
    converted_format = serializers.ChoiceField(choices=ConversionRecord.FORMAT_CHOICES)  # Restrict format choices

    class Meta:
        model = ConversionRecord
        fields = ["id", "file","file_name", "converted_format", "upload_date"]
        read_only_fields = ["file_name", "upload_date"]

    def create(self, validated_data):
        uploaded_file = validated_data.pop("file")  # Extract file
        validated_data["file_name"] = uploaded_file.name  # Save original filename
        return super().create(validated_data) 
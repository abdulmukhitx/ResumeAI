"""
Custom renderer for DRF browsable API upload endpoint
"""
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from django.template.loader import render_to_string


class CustomUploadAPIRenderer(BrowsableAPIRenderer):
    """Custom renderer for upload endpoints to show a file upload form."""
    
    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        
        # Add custom context for upload endpoints
        view = renderer_context.get('view')
        if hasattr(view, 'action') or 'upload' in str(view.__class__.__name__).lower():
            context['is_upload_endpoint'] = True
            context['upload_help'] = {
                'method': 'POST',
                'content_type': 'multipart/form-data',
                'required_fields': ['file'],
                'file_types': ['.pdf'],
                'max_size': '10MB'
            }
        
        return context
    
    def get_form(self, view, method, request):
        """Override to provide file upload form for POST requests."""
        if method == 'POST' and 'upload' in str(view.__class__.__name__).lower():
            return self._get_upload_form()
        return super().get_form(view, method, request)
    
    def _get_upload_form(self):
        """Return a custom upload form."""
        return """
        <form enctype="multipart/form-data" method="post">
            <div class="form-group">
                <label for="file">Resume File (PDF only):</label>
                <input type="file" name="file" accept=".pdf" required class="form-control" />
                <small class="form-text text-muted">
                    Select a PDF resume file (max 10MB). The file will be processed automatically.
                </small>
            </div>
            <button type="submit" class="btn btn-primary">Upload Resume</button>
        </form>
        <div class="alert alert-info mt-3">
            <h5>📋 Upload Instructions:</h5>
            <ul>
                <li><strong>Authentication:</strong> You must be logged in (JWT token required)</li>
                <li><strong>File Type:</strong> PDF files only</li>
                <li><strong>File Size:</strong> Maximum 10MB</li>
                <li><strong>Processing:</strong> Analysis starts automatically after upload</li>
            </ul>
            <h6>✅ Expected Response (Success):</h6>
            <pre><code>{
  "success": true,
  "message": "Resume uploaded successfully",
  "resume": {
    "id": 123,
    "filename": "resume.pdf",
    "status": "processing",
    "uploaded_at": "2025-06-28T16:30:00Z",
    "processor": "v4_ultra_safe_ascii_only"
  }
}</code></pre>
        </div>
        """

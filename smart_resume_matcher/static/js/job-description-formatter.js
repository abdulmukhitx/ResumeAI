// Job Description Formatter
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the job detail page
    const jobDescriptionElement = document.querySelector('.job-description');
    const jobRequirementsElement = document.querySelector('.job-requirements');
    
    if (jobDescriptionElement || jobRequirementsElement) {
        // Get the job ID from the URL
        const url = window.location.pathname;
        const jobId = url.split('/').filter(Boolean).pop();
        
        if (jobId && !isNaN(jobId)) {
            // Fetch the formatted job description from the API
            fetch(`/jobs/api/job-description/${jobId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update description if it exists
                        if (jobDescriptionElement && data.formatted_description) {
                            jobDescriptionElement.innerHTML = formatTextForHTML(data.formatted_description);
                        }
                        
                        // Update requirements if they exist
                        if (jobRequirementsElement && data.formatted_requirements) {
                            jobRequirementsElement.innerHTML = formatTextForHTML(data.formatted_requirements);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error fetching formatted job description:', error);
                });
        }
    }
});

/**
 * Format text for HTML display
 * Converts markdown-like syntax to HTML
 */
function formatTextForHTML(text) {
    if (!text) return '';
    
    // Convert paragraphs
    text = text.replace(/\n\n/g, '</p><p>');
    
    // Convert headings (## Heading)
    text = text.replace(/## (.*?)\n/g, '<h5>$1</h5>');
    
    // Convert bullet points
    text = text.replace(/• (.*?)\n/g, '<li>$1</li>');
    
    // Wrap bullet point lists in <ul> tags
    if (text.includes('<li>')) {
        const parts = text.split('<li>');
        let result = parts[0];
        
        if (parts.length > 1) {
            result += '<ul><li>' + parts.slice(1).join('<li>');
            result = result.replace(/<\/li>([^<]*?)(?=<li>|$)/g, '</li>$1');
            result += '</ul>';
        }
        
        text = result;
    }
    
    // Wrap in paragraphs if not already
    if (!text.startsWith('<p>')) {
        text = '<p>' + text + '</p>';
    }
    
    return text;
}

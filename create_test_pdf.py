#!/usr/bin/env python3
"""
Create a test PDF with potentially problematic characters for testing
"""
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    def create_test_pdf():
        filename = "/tmp/test_encoding_resume.pdf"
        
        # Create a canvas
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add some text with potentially problematic characters
        text_lines = [
            "John Doe - Software Engineer",
            "Email: john.doe@email.com",
            "Phone: (555) 123-4567",
            "",
            "EXPERIENCE:",
            "• Senior Developer at Tech Corp (2020-2023)",
            "• Worked with Python, JavaScript, and SQL",
            "• Led team of 5 developers",
            "",
            "SKILLS:",
            "• Programming: Python, JavaScript, Java, C++",
            "• Databases: PostgreSQL, MySQL, MongoDB", 
            "• Frameworks: Django, React, Angular",
            "• Tools: Git, Docker, Kubernetes",
            "",
            "EDUCATION:",
            "• BS Computer Science - University (2018)",
            "• Relevant coursework: Data Structures, Algorithms",
            "",
            "Special characters test: café, résumé, naïve",
            "Unicode test: ñoño, François, München"
        ]
        
        # Write text to PDF
        y_position = 750
        for line in text_lines:
            try:
                c.drawString(50, y_position, line)
            except:
                # If there's an encoding issue, write a safe version
                safe_line = ''.join(char for char in line if ord(char) < 128)
                c.drawString(50, y_position, safe_line)
            y_position -= 20
        
        c.save()
        print(f"Test PDF created: {filename}")
        return filename
    
    if __name__ == "__main__":
        create_test_pdf()
        
except ImportError:
    print("reportlab not installed. Creating a simple text file instead.")
    filename = "/tmp/test_resume.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("""John Doe - Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

EXPERIENCE:
• Senior Developer at Tech Corp (2020-2023)
• Worked with Python, JavaScript, and SQL
• Led team of 5 developers

SKILLS:
• Programming: Python, JavaScript, Java, C++
• Databases: PostgreSQL, MySQL, MongoDB
• Frameworks: Django, React, Angular
• Tools: Git, Docker, Kubernetes

EDUCATION:
• BS Computer Science - University (2018)
• Relevant coursework: Data Structures, Algorithms

Special characters test: café, résumé, naïve
Unicode test: ñoño, François, München
""")
    print(f"Test text file created: {filename}")

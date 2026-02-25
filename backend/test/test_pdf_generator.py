import os
import pytest
import shutil
from infrastructure.pdf_generator import PDFGenerator

@pytest.fixture
def test_output_dir(tmp_path):
    """Creates a temporary directory for test PDFs."""
    d = tmp_path / "test_pdfs"
    d.mkdir()
    return str(d)

@pytest.mark.asyncio
async def test_generate_pdf_success(test_output_dir):
    """Verify that a PDF is actually created on disk with correct metadata."""
    generator = PDFGenerator(output_dir=test_output_dir)
    
    content = "This is a test report content.\nLine 2 of the report."
    metadata = {
        "title": "Test Civic Report",
        "author": "Mudda AI",
        "issue_id": "ISSUE-123"
    }
    
    result = await generator.generate(content, metadata)
    
    # Verify return values
    assert "file_path" in result
    assert result["filename"] == "test_civic_report.pdf"
    assert result["size_bytes"] > 0
    assert result["metadata"] == metadata
    
    # Verify file exists on disk
    assert os.path.exists(result["file_path"])
    assert result["file_path"].endswith(".pdf")
    
    # Basic fpdf2 sanity check: file header should be %PDF
    with open(result["file_path"], "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"

@pytest.mark.asyncio
async def test_generate_pdf_custom_filename(test_output_dir):
    """Verify custom filename support."""
    generator = PDFGenerator(output_dir=test_output_dir)
    custom_name = "custom_report_name.pdf"
    
    result = await generator.generate("Content", {"title": "Title"}, filename=custom_name)
    
    assert result["filename"] == custom_name
    assert os.path.basename(result["file_path"]) == custom_name

def test_pdf_generator_init_creates_dir():
    """Verify that init creates the output directory if it doesn't exist."""
    new_dir = os.path.join(os.getcwd(), "temp_auto_create_dir")
    if os.path.exists(new_dir):
        shutil.rmtree(new_dir)
        
    try:
        generator = PDFGenerator(output_dir=new_dir)
        assert os.path.exists(new_dir)
    finally:
        if os.path.exists(new_dir):
            shutil.rmtree(new_dir)

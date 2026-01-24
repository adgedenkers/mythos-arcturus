"""
Prompts for document/text analysis
"""

READ_DOCUMENT = """Extract all readable text from this document.
Preserve the structure and formatting as much as possible.
Note any text that's unclear or partially visible."""


SUMMARIZE_DOCUMENT = """Read this document and provide:
1. Document type (letter, form, certificate, etc.)
2. Key information (names, dates, numbers)
3. Brief summary of contents
4. Any notable or important details"""


GENEALOGY_DOCUMENT = """This is a genealogical document. Extract:
- Names (with roles: parent, child, spouse, witness)
- Dates (birth, death, marriage, etc.)
- Places mentioned
- Relationships indicated
- Document type and date

Format as structured data:
{
  "document_type": "",
  "document_date": "",
  "people": [
    {"name": "", "role": "", "dates": {}, "notes": ""}
  ],
  "places": [],
  "relationships": [],
  "other_details": ""
}"""


HANDWRITING_TRANSCRIPTION = """Transcribe the handwritten text in this image.
- Use [unclear] for words you can't read
- Preserve line breaks where apparent
- Note any crossed-out or corrected text
- Include any marginalia or notes"""


RECEIPT_EXTRACTION = """Extract information from this receipt:
- Store/vendor name
- Date and time
- Items and prices
- Subtotal, tax, total
- Payment method
- Any other relevant details

Format as JSON."""

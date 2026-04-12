from pypdf import PdfReader, PdfWriter

input_pdf = "output-2.pdf"
output_pdf = "sample_protected.pdf"
password = "test123"

reader = PdfReader(input_pdf)
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.encrypt(password)

with open(output_pdf, "wb") as f:
    writer.write(f)

print(f"Created {output_pdf} with password: {password}")
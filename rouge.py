import evaluate
import csv
from PyPDF2 import PdfReader

def load_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        text.extend(page.extract_text().splitlines())
    return [line.strip() for line in text if line.strip()]

predictions = load_pdf_text('predictions.pdf')
references = load_pdf_text('reference.pdf')

min_len = min(len(predictions), len(references))
predictions = predictions[:min_len]
references = references[:min_len]

references = [[ref] for ref in references]

rouge = evaluate.load("rouge")
results = rouge.compute(predictions=predictions, references=references)

print("ROUGE-1 Score:", results['rouge1'])
print("ROUGE-2 Score:", results['rouge2'])
print("ROUGE-L Score:", results['rougeL'])
print("ROUGE-LSum Score:", results['rougeLsum'])

with open('rouge_results.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Metric', 'F1-score'])
    writer.writerow(['ROUGE-1', results['rouge1']])
    writer.writerow(['ROUGE-2', results['rouge2']])
    writer.writerow(['ROUGE-L', results['rougeL']])
    writer.writerow(['ROUGE-LSum', results['rougeLsum']])



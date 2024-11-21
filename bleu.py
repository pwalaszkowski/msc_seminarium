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

bleu = evaluate.load("bleu")
results = bleu.compute(predictions=predictions, references=references)

print("BLEU Score:", results['bleu'])
print("Precisions:", results['precisions'])
print("Brevity Penalty:", results['brevity_penalty'])
print("Length Ratio:", results['length_ratio'])
print("Translation Length:", results['translation_length'])
print("Reference Length:", results['reference_length'])

with open('bleu_results.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Metric', 'Score'])
    writer.writerow(['BLEU', results['bleu']])
    writer.writerow(['Precisions (n-gram 1-4)', results['precisions']])
    writer.writerow(['Brevity Penalty', results['brevity_penalty']])
    writer.writerow(['Length Ratio', results['length_ratio']])
    writer.writerow(['Translation Length', results['translation_length']])
    writer.writerow(['Reference Length', results['reference_length']])

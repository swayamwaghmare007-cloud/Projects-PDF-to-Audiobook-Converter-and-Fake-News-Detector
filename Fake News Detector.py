import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF for PDF extraction
from PIL import Image
import pytesseract
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Specify Tesseract path (update if different)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class FakeNewsDetectorApp:
    def __init__(self, root):
        self.root = root
        root.title('Fake News Detector')
        root.geometry('700x500')
        # Top bar
        top = tk.Frame(root)
        top.pack(fill='x', padx=8, pady=6)
        tk.Button(top, text='Upload File or Screenshot', command=self.upload_file).pack(side='left')
        self.verify_btn = tk.Button(top, text='Verify', command=self.verify_news, state='disabled')
        self.verify_btn.pack(side='left', padx=6)
        # Text area
        self.text_box = scrolledtext.ScrolledText(root, wrap='word')
        self.text_box.pack(fill='both', expand=True, padx=8, pady=8)
        self.current_text = ''
        self.model = self.load_or_train_model()

    def load_or_train_model(self):
        model_path = r'D:\python internship\A-Chatbot-using-if-else\fake_news_model.joblib'
        if os.path.exists(model_path):
            print("Loading existing model...")
            return joblib.load(model_path)

        # Train model if not found
        print("Training new model...")
        fake_path = r'D:\python internship\News _dataset\Fake.csv'
        true_path = r'D:\python internship\News _dataset\True.csv'
        if not os.path.exists(fake_path) or not os.path.exists(true_path):
            messagebox.showerror('Error', f'Dataset files not found at:\n{fake_path}\n{true_path}\nPlease download Fake.csv and True.csv from Kaggle.')
            return None

        # Load and combine CSVs
        fake = pd.read_csv(fake_path)
        true = pd.read_csv(true_path)
        fake['label'] = 'FAKE'
        true['label'] = 'REAL'
        fake['text'] = fake['title'].fillna('') + ' ' + fake['text'].fillna('')
        true['text'] = true['title'].fillna('') + ' ' + true['text'].fillna('')
        df = pd.concat([fake[['text', 'label']], true[['text', 'label']]])
        df['label'] = df['label'].map({'REAL': 1, 'FAKE': 0})

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

        # Train model
        model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1,2))),
            ('clf', LogisticRegression(max_iter=1000))
        ])
        model.fit(X_train, y_train)

        # Evaluate
        preds = model.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, preds))
        print("\nClassification Report:")
        print(classification_report(y_test, preds, target_names=['Fake', 'Real']))

        # Save model
        joblib.dump(model, model_path)
        print(f"✅ Model saved as {model_path}")
        return model

    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf'), ('Image Files', '*.png;*.jpg;*.jpeg'), ('Text Files', '*.txt')])
        if not path:
            return
        try:
            text = ''
            if path.lower().endswith('.pdf'):
                doc = fitz.open(path)
                for page in doc:
                    text += page.get_text().strip() + '\n'
                doc.close()
            elif path.lower().endswith('.txt'):
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif path.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(path)
                text = pytesseract.image_to_string(img)
            self.current_text = text
            self.text_box.delete('1.0', tk.END)
            self.text_box.insert(tk.END, self.current_text)
            self.verify_btn.config(state='normal')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to extract text:\n{e}')

    def verify_news(self):
        text = self.text_box.get('1.0', tk.END).strip()
        if not text:
            messagebox.showinfo('Empty', 'No text to verify.')
            return
        if self.model is None:
            messagebox.showerror('Model Error', 'Model not loaded. Please ensure dataset files are available and try again.')
            return
        pred = self.model.predict([text])[0]
        result = 'Real' if pred == 1 else 'Fake'
        messagebox.showinfo('Verification', f'This news is predicted to be: {result}')

if __name__ == '__main__':
    root = tk.Tk()
    app = FakeNewsDetectorApp(root)
    root.mainloop()
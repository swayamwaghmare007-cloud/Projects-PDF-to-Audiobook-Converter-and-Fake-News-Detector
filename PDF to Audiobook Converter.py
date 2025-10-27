import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF
import pyttsx3
import threading
import os
import subprocess

# PDF to Audiobook Converter
class PDFToAudiobookApp:
    def __init__(self, root):
        self.root = root
        root.title('PDF to Audiobook - Python 3.14 Version')
        root.geometry('700x500')
        # Top bar
        top = tk.Frame(root)
        top.pack(fill='x', padx=8, pady=6)
        tk.Button(top, text='Open PDF', command=self.open_pdf).pack(side='left')
        self.play_btn = tk.Button(top, text='Play', command=self.play_text, state='disabled')
        self.play_btn.pack(side='left', padx=6)
        self.save_btn = tk.Button(top, text='Save Audio', command=self.save_audio, state='disabled')
        self.save_btn.pack(side='left')
        tk.Label(top, text='Rate:').pack(side='left', padx=(12,0))
        self.rate_var = tk.IntVar(value=150)
        tk.Spinbox(top, from_=100, to=300, textvariable=self.rate_var, width=6).pack(side='left')
        # Text area
        self.text_box = scrolledtext.ScrolledText(root, wrap='word')
        self.text_box.pack(fill='both', expand=True, padx=8, pady=8)
        self.engine = pyttsx3.init()
        self.current_text = ''
    
    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf')])
        if not path:
            return
        try:
            doc = fitz.open(path)
            full_text = []
            for page in doc:
                txt = page.get_text().strip()
                if txt:
                    full_text.append(txt)
            doc.close()
            self.current_text = '\n\n'.join(full_text)
            self.text_box.delete('1.0', tk.END)
            self.text_box.insert(tk.END, self.current_text)
            self.play_btn.config(state='normal')
            self.save_btn.config(state='normal')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open PDF:\n{e}')
    
    def play_text(self):
        text = self.text_box.get('1.0', tk.END).strip()
        if not text:
            messagebox.showinfo('Empty', 'No text to play.')
            return
        rate = self.rate_var.get()
        threading.Thread(target=self._speak, args=(text, rate), daemon=True).start()
    
    def _speak(self, text, rate):
        self.engine.setProperty('rate', rate)
        for i in range(0, len(text), 2000):
            self.engine.say(text[i:i+2000])
            self.engine.runAndWait()
    
    def save_audio(self):
        text = self.text_box.get('1.0', tk.END).strip()
        if not text:
            messagebox.showinfo('Empty', 'No text to save.')
            return
        out_path = filedialog.asksaveasfilename(defaultextension='.mp3',
                                               filetypes=[('MP3', '*.mp3'), ('WAV', '*.wav')])
        if not out_path:
            return
        try:
            rate = self.rate_var.get()
            self.engine.setProperty('rate', rate)
            wav_temp = 'temp_output.wav'
            self.engine.save_to_file(text, wav_temp)
            self.engine.runAndWait()
            if out_path.lower().endswith('.mp3'):
                result = subprocess.run(
                    ['ffmpeg', '-i', wav_temp, '-acodec', 'mp3', '-y', out_path],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    raise Exception(f"FFmpeg error: {result.stderr}")
                os.remove(wav_temp)
            else:
                os.replace(wav_temp, out_path)
            messagebox.showinfo('Saved', f'Audio saved to:\n{out_path}')
        except Exception as e:
            messagebox.showerror('Save Error', str(e))
            if os.path.exists(wav_temp):
                os.remove(wav_temp)

if __name__ == '__main__':
    root = tk.Tk()
    app = PDFToAudiobookApp(root)
    root.mainloop()
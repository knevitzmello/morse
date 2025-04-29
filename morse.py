import time
import threading
import simpleaudio as sa
import tkinter as tk
import queue
import numpy as np

# Dicionário Morse
MORSE_CODE_DICT = {
    '.-': 'A',    '-...': 'B',  '-.-.': 'C',  '-..': 'D',   '.': 'E',
    '..-.': 'F',  '--.': 'G',   '....': 'H',  '..': 'I',    '.---': 'J',
    '-.-': 'K',   '.-..': 'L',  '--': 'M',    '-.': 'N',    '---': 'O',
    '.--.': 'P',  '--.-': 'Q',  '.-.': 'R',   '...': 'S',   '-': 'T',
    '..-': 'U',   '...-': 'V',  '.--': 'W',   '-..-': 'X',  '-.--': 'Y',
    '--..': 'Z',  '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9'
}

LETTER_TIMEOUT = 0.5  # segundos
DOT_TONE_DURATION = 0.1
DASH_TONE_DURATION = 0.2
PAUSA_ENTRE_LETRAS = 0.5
PAUSA_ENTRE_SINAIS = 0.1
FREQ_DOT = 600
FREQ_DASH = 600

current_sequence = ''
last_input_time = time.time()
lock = threading.Lock()
clear = False

sound_queue = queue.Queue()

playback_queue = queue.Queue()
playback_running = threading.Event()
playback_paused = threading.Event()

TEXT_TO_MORSE = {
    'A': '.-',   'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.',  'H': '....', 'I': '..',  'J': '.---',
    'K': '-.-',  'L': '.-..', 'M': '--',   'N': '-.',  'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.',  'S': '...', 'T': '-',
    'U': '..-',  'V': '...-', 'W': '.--',  'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----','1': '.----','2': '..---','3': '...--',
    '4': '....-','5': '.....','6': '-....','7': '--...','8': '---..',
    '9': '----.'
}

def play_tone(freq, duration):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * t * 2 * np.pi)
    audio = (tone * 32767).astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, sample_rate)
    play_obj.wait_done()

def sound_player():
    while True:
        freq, duration = sound_queue.get()
        play_tone(freq, duration)
        sound_queue.task_done()

def monitor_timeout(output_label, message_label):
    global current_sequence, last_input_time, clear
    message = ''
    while True:
        time.sleep(0.1)
        if clear:
            message = ''
        if time.time() - last_input_time > LETTER_TIMEOUT and current_sequence:
            with lock:
                letra = MORSE_CODE_DICT.get(current_sequence, '?')
                print(f"{current_sequence} -> {letra}")
                message += letra
                current_sequence = ''
                output_label.after(0, lambda: output_label.config(text=f"Última letra: {letra}"))
                message_label.after(0, lambda: message_label.config(text=f"Mensagem: {message}"))

def on_click(event, output_label):
    global current_sequence, last_input_time
    widget_class = event.widget.winfo_class()
    if widget_class in ['Button', 'Entry']:
        return  # Ignora o clique em botões ou caixas de texto
    with lock:
        if event.num == 1:
            current_sequence += '.'
            sound_queue.put((FREQ_DOT, DOT_TONE_DURATION))
        elif event.num == 3:
            current_sequence += '-'
            sound_queue.put((FREQ_DASH, DASH_TONE_DURATION))
        last_input_time = time.time()
        output_label.config(text=f"Sequência: {current_sequence}")

def clear_message(message_label):
    global clear
    clear = True
    time.sleep(0.3)
    clear = False
    message = ''
    with lock:
        message_label.after(0, lambda: message_label.config(text=f"Mensagem: {message}"))

def text_to_morse(text):
    result = []
    for char in text.upper():
        if char in TEXT_TO_MORSE:
            result.append(TEXT_TO_MORSE[char])
    return ' '.join(result)

def playback_worker():
    while True:
        playback_running.wait()
        if playback_paused.is_set():
            time.sleep(0.1)
            continue
        try:
            time.sleep(PAUSA_ENTRE_SINAIS)
            symbol = playback_queue.get_nowait()
            if symbol == '.':
                play_tone(FREQ_DOT, DOT_TONE_DURATION)
            elif symbol == '-':
                play_tone(FREQ_DASH, DASH_TONE_DURATION)
            elif symbol == ' ':
                time.sleep(PAUSA_ENTRE_LETRAS)  # pausa entre letras
            playback_queue.task_done()
        except queue.Empty:
            playback_running.clear()

def start_playback(text_entry):
    text = text_entry.get()
    if text.strip():
        morse_sequence = text_to_morse(text)
        print(f"Reproduzindo: {morse_sequence}")
        for symbol in morse_sequence:
            playback_queue.put(symbol)
        playback_running.set()
        playback_paused.clear()

def pause_playback():
    if playback_running.is_set():
        playback_paused.set()

def resume_playback():
    if playback_running.is_set():
        playback_paused.clear()

def stop_playback():
    playback_running.clear()
    with playback_queue.mutex:
        playback_queue.queue.clear()

def main():
    root = tk.Tk()
    root.title("Morse Translator")
    root.geometry("500x500")
    root.configure(bg="black")

    title = tk.Label(root, text="Clique:\nEsquerdo = ponto, Direito = traço",
                     font=("Arial", 14), bg="black", fg="white")
    title.pack(pady=10)

    output_label = tk.Label(root, text="Esperando...", font=("Arial", 16), bg="black", fg="cyan")
    output_label.pack(pady=10)

    message_label = tk.Label(root, text="Mensagem: ", font=("Arial", 14), bg="black", fg="yellow")
    message_label.pack(pady=10)

    clear_button = tk.Button(root, text="Limpar Mensagem", command=lambda: clear_message(message_label))
    clear_button.pack(pady=5)

    tk.Label(root, text="Digite um texto para reproduzir:", font=("Arial", 12), bg="black", fg="white").pack(pady=10)
    text_entry = tk.Entry(root, font=("Arial", 14))
    text_entry.pack(pady=5)

    play_button = tk.Button(root, text="Play", command=lambda: start_playback(text_entry))
    play_button.pack(pady=5)

    stop_button = tk.Button(root, text="Stop", command=stop_playback)
    stop_button.pack(pady=5)

    root.bind("<Button-1>", lambda e: on_click(e, output_label))
    root.bind("<Button-3>", lambda e: on_click(e, output_label))

    threading.Thread(target=sound_player, daemon=True).start()
    threading.Thread(target=monitor_timeout, args=(output_label, message_label), daemon=True).start()
    threading.Thread(target=playback_worker, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()

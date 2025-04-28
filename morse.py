import time
import threading
import simpleaudio as sa
import tkinter as tk
import queue
import numpy as np

# Dicionário de código Morse
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

# Configurações
LETTER_TIMEOUT = 1.0  # segundos sem input para considerar fim de letra
DOT_TONE_DURATION = 0.1  # duração do som do ponto
DASH_TONE_DURATION = 0.2  # duração do som do traço
FREQ_DOT = 600        # frequência para ponto
FREQ_DASH = 600       # frequência para traço

current_sequence = ''
last_input_time = time.time()
lock = threading.Lock()

# Fila para sons
sound_queue = queue.Queue()

# Função para gerar e tocar o som
def play_tone(freq, duration):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * t * 2 * np.pi)
    audio = (tone * 32767).astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, sample_rate)
    play_obj.wait_done()

# Worker que toca os sons na ordem
def sound_player():
    while True:
        freq, duration = sound_queue.get()
        play_tone(freq, duration)
        sound_queue.task_done()

# Função para verificar fim de letra
def monitor_timeout(output_label):
    global current_sequence, last_input_time
    while True:
        time.sleep(0.1)
        if time.time() - last_input_time > LETTER_TIMEOUT and current_sequence:
            with lock:
                letra = MORSE_CODE_DICT.get(current_sequence, '?')
                print(f"{current_sequence} -> {letra}")
                current_sequence = ''
                output_label.after(0, lambda: output_label.config(text=f"Última letra: {letra}"))

# Evento de clique no Tkinter
def on_click(event, output_label):
    global current_sequence, last_input_time
    with lock:
        if event.num == 1:  # Botão esquerdo
            current_sequence += '.'
            sound_queue.put((FREQ_DOT, DOT_TONE_DURATION))
        elif event.num == 3:  # Botão direito
            current_sequence += '-'
            sound_queue.put((FREQ_DASH, DASH_TONE_DURATION))
        last_input_time = time.time()
        output_label.config(text=f"Sequência: {current_sequence}")

# Criação da janela
def main():
    root = tk.Tk()
    root.title("Morse Translator")
    root.geometry("400x300")
    root.configure(bg="black")

    title = tk.Label(root, text="Clique aqui:\nEsquerdo = ponto, Direito = traço",
                     font=("Arial", 14), bg="black", fg="white")
    title.pack(pady=20)

    output_label = tk.Label(root, text="Esperando...", font=("Arial", 16), bg="black", fg="cyan")
    output_label.pack(pady=20)

    root.bind("<Button-1>", lambda e: on_click(e, output_label))  # Botão esquerdo
    root.bind("<Button-3>", lambda e: on_click(e, output_label))  # Botão direito

    # Thread para tocar os sons da fila
    threading.Thread(target=sound_player, daemon=True).start()

    # Thread para monitorar timeout
    threading.Thread(target=monitor_timeout, args=(output_label,), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()

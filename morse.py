import time
import threading
import simpleaudio as sa
import tkinter as tk
import queue
import numpy as np

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
LETTER_TIMEOUT = 0.5  # segundos
DOT_TONE_DURATION = 0.1
DASH_TONE_DURATION = 0.2
FREQ_DOT = 600
FREQ_DASH = 600

current_sequence = ''
last_input_time = time.time()
mensagem = ''  
lock = threading.Lock()

sound_queue = queue.Queue()

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
    global current_sequence, last_input_time, mensagem
    while True:
        time.sleep(0.1)
        if time.time() - last_input_time > LETTER_TIMEOUT and current_sequence:
            with lock:
                letra = MORSE_CODE_DICT.get(current_sequence, '?')
                print(f"{current_sequence} -> {letra}")
                mensagem += letra
                current_sequence = ''
                output_label.after(0, lambda: output_label.config(text=f"Última letra: {letra}"))
                message_label.after(0, lambda: message_label.config(text=f"Mensagem: {mensagem}"))

def on_click(event, output_label):
    global current_sequence, last_input_time

    if event.widget != event.widget.winfo_toplevel():
        return

    with lock:
        if event.num == 1:  # Botão esquerdo
            current_sequence += '.'
            sound_queue.put((FREQ_DOT, DOT_TONE_DURATION))
        elif event.num == 3:  # Botão direito
            current_sequence += '-'
            sound_queue.put((FREQ_DASH, DASH_TONE_DURATION))
        last_input_time = time.time()
        output_label.config(text=f"Sequência: {current_sequence}")


def limpar_mensagem(message_label, output_label):
    global mensagem
    with lock:
        mensagem = ''
        message_label.config(text="Mensagem: (vazia)")
        output_label.config(text="Esperando...")

def main():
    root = tk.Tk()
    root.title("Morse Translator")
    root.geometry("400x350")
    root.configure(bg="black")

    title = tk.Label(root, text="Clique na janela para escrever:\nEsquerdo = ponto, Direito = traço",
                     font=("Arial", 14), bg="black", fg="white")
    title.pack(pady=10)

    output_label = tk.Label(root, text="Esperando...", font=("Arial", 16), bg="black", fg="cyan")
    output_label.pack(pady=10)

    message_label = tk.Label(root, text="Mensagem: (vazia)", font=("Arial", 16), bg="black", fg="lime")
    message_label.pack(pady=10)

    clear_button = tk.Button(root, text="Limpar Mensagem", font=("Arial", 12),
                              command=lambda: limpar_mensagem(message_label, output_label),
                              bg="red", fg="white")
    clear_button.pack(pady=10)

    root.bind("<Button-1>", lambda e: on_click(e, output_label))
    root.bind("<Button-3>", lambda e: on_click(e, output_label))

    threading.Thread(target=sound_player, daemon=True).start()
    threading.Thread(target=monitor_timeout, args=(output_label, message_label), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()

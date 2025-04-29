# Tradutor morse em python

Este é um tradutor de código Morse feito com Python usando uma interface gráfica (Tkinter).

O usuário pode clicar na janela para construir uma sequência em Morse:
- **Clique esquerdo**: ponto (`.`)
- **Clique direito**: traço (`-`)

Após um pequeno intervalo de tempo sem cliques, a sequência digitada é automaticamente traduzida em uma letra, exibida na tela, e a mensagem completa é montada.

O programa também reproduz sons para cada ponto e traço usando a biblioteca **SimpleAudio**.

---

## Funcionalidades
- Tradução de código Morse em tempo real.
- Sons distintos para ponto e traço.
- Exibição contínua da mensagem decodificada.
- Edição do tempo de timeout
- Botão **"Limpar Mensagem"** para reiniciar a digitação.
- Tradução para morse de texto inserido

---

## Requisitos
- Python **3.7** ou superior
- Bibliotecas Python:
  - `numpy`
  - `simpleaudio`
  - `tkinter`

### Instalação das dependências
```bash
pip install numpy simpleaudio

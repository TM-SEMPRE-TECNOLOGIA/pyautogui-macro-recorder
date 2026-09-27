<div align="center">

# ⚡ PyAutoGUI Macro Studio

### Automação de Tarefas em Lote com Gravador Visual de Mouse, Teclado & Scroll

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#)

<p align="center">
  <b>Grave qualquer rotina repetitiva no seu computador com 1 clique e reproduza em lote na velocidade que desejar.</b>
</p>

</div>

---

## 🎯 Por que o Macro Studio?

Muitas vezes precisamos repetir uma tarefa massiva no computador (clicar com o botão direito, selecionar um menu, copiar, colar, rolar a página ou preencher formulários repetitivos). 

Criar scripts do `pyautogui` do zero calculando manualmente coordenadas $(X, Y)$ é demorado. O **PyAutoGUI Macro Studio** resolve isso oferecendo uma interface visual moderna onde você aperta **Capturar**, executa a ação normalmente no computador, e aperta **Finalizar**. 

O app registra tudo, gera o código Python limpo em tempo real e permite executar ciclos em lote instantaneamente.

---

## ✨ Recursos Principais

- 🖱️ **Captura Completa de Mouse**:
  - Clique esquerdo, clique direito e clique do meio.
  - Movimentos e arrastes (drag & drop opcional).
  - **Rolagem da rodinha (Scroll)** com calibração nativa para Windows (120 ticks/passo).
- ⌨️ **Teclado & Atalhos**: Captura teclas individuais, combinações e atalhos (`Ctrl+C`, `Ctrl+V`, `Enter`, etc.).
- 🔁 **Execução em Lote Configurável**:
  - Defina o número de repetições (ex: 10, 50, 1000 ciclos).
  - Multiplicador de velocidade (`0.5x`, `1.0x Normal`, `2.0x`, `Sem delay`).
  - Intervalo de descanso customizável entre ciclos.
- 🛡️ **Mecanismos de Segurança Antifalha**:
  - **Parada de Emergência com Tecla `ESC`**: Aborta a execução imediatamente a qualquer momento.
  - **FailSafe Nativo PyAutoGUI**: Puxe o mouse para o canto superior esquerdo da tela (`0, 0`) para travar o robô.
  - **Countdown de 3 Segundos**: Permite alternar para a janela certa antes de a automação começar.
- 💾 **Persistência & Exportação**:
  - Salve e carregue rotinas salvas em formato `.json`.
  - Exporte scripts Python independentes prontos para rodar via terminal ou em servidores sem interface gráfica.
- 🪟 **Modo Silencioso no Windows**:
  - Inicia sem abrir a janela preta de terminal (`main.pyw` / inicializador silencioso).

---

## 📸 Demonstração da Interface

```text
+-----------------------------------------------------------------------------------+
| ⚡ Macro Studio  [ ● Pronto para capturar ]                     [ 12 Ações ]      |
+------------------------------------+----------------------------------------------+
| [ CONTROLES ]                      |  [ 📋 Ações Capturadas ]  [ 🐍 Código Python ]|
|                                    |                                              |
| ⏺ Iniciar Captura                  |  #  | TEMPO  | TIPO        | DETALHES        |
| [x] Capturar arraste/movimento     |  1  | +0.45s | mouse_click | Botão Direito    |
|                                    |  2  | +1.20s | mouse_scroll| Scroll -120      |
| [ EXECUÇÃO EM LOTE ]               |  3  | +0.80s | key_press   | Tecla 'enter'    |
| Repetições: [ 50  ]                |                                              |
| Velocidade: [ 2.0x ]               |                                              |
| Pausa entre ciclos: [ 1.0s ]       |                                              |
|                                    |                                              |
| ▶ Executar Macro                   |                                              |
| ⏹ Interromper (ESC)                |                                              |
|                                    |                                              |
| 💾 Salvar (.json)  📂 Carregar     |                                              |
| 📄 Exportar Script .py             |                                              |
+------------------------------------+----------------------------------------------+
```

---

## 🚀 Como Instalar e Rodar

### Pré-requisitos
- Python 3.10 ou superior instalado.

### 1. Clonar o Repositório
```bash
git clone https://github.com/TM-SEMPRE-TECNOLOGIA/pyautogui-macro-recorder.git
cd pyautogui-macro-recorder
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar a Aplicação

#### 🔹 Opção A (Sem Terminal - Recomendado no Windows):
Dê um duplo clique em:
- **`abrir_sem_terminal.vbs`** ou
- **`iniciar.bat`** ou
- **`main.pyw`**

#### 🔹 Opção B (Via Linha de Comando):
```bash
python main.py
```

---

## 🛠️ Tecnologias Utilizadas

- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Interface gráfica moderna em Dark Mode.
- **[PyAutoGUI](https://github.com/asweigart/pyautogui)** - Controle programático de mouse e teclado.
- **[pynput](https://github.com/moses-palmer/pynput)** - Monitoramento global de eventos de hardware em background.

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para obter mais detalhes.

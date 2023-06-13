import math
from typing import TYPE_CHECKING

from constants import SMALL_FONT_SIZE
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QPushButton
from utils import convertToNumber, isEmpty, isNumOrDot, isValidNumber

# Uma variavel que é True se eu estou fazendo apenas typechecking
# e False se eu não estou fazendo typechecking
if TYPE_CHECKING:
    from display import Display
    from info import Info
    from main_window import MainWindow
# Evita circular imports, mas preciso colocar entre aspas a classe
# veja no __init__ do ButtonsGrid, coloquei 'Display' e 'Info'
# evitando esse possível erro e facilitando para mim


class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        font = self.font()
        font.setPixelSize(SMALL_FONT_SIZE)
        self.setFont(font)
        self.setMinimumSize(75, 75)


class ButtonsGrid(QGridLayout):
    def __init__(
            self, display: 'Display', info: 'Info', window: 'MainWindow',
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Mascara de botões
        self._gridMask = [
            ['c', 'D', '^', '/'],
            ['N', 'sqrt', '%', '!'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['',  '0', '.', '='],
        ]
        # Outras informações
        self.info = info
        self.window = window
        self.display = display
        self._equation = ''
        self._equationInitialValue = "Sua conta"
        self._leftNum = None
        self._rightNum = None
        self._operator = None
        self._makeGrid()

    @property
    def equation(self):
        return self._equation

    @equation.setter
    def equation(self, value):
        self._equation = value
        self.info.setText(value)

    def _makeGrid(self):
        self.display.eqPressed.connect(self._eq)
        self.display.delPressed.connect(self._backspace)
        self.display.clearPressed.connect(self._clear)
        self.display.inputPressed.connect(self._insertToDisplay)
        self.display.operatorPressed.connect(self._configLeftOp)
        self.display.inversePressed.connect(self._invertNumber)

        for i, row in enumerate(self._gridMask):
            for j, buttonText in enumerate(row):

                if buttonText == "":
                    continue

                if not buttonText == '0':

                    button = Button(buttonText)

                    if not isNumOrDot(buttonText) and not isEmpty(buttonText):
                        button.setProperty("cssClass", "specialButton")
                        self._configSpecialButton(button)

                    self.addWidget(button, i, j)  # ij, linha coluna

                    slot = self._makeSlot(
                        self._insertToDisplay, buttonText)
                    self._connectButtonClicked(button, slot)

                else:
                    button0 = Button(buttonText)
                    self.addWidget(button0, i, j-1, 1, 2,)

                    button0Slot = self._makeSlot(
                        self._insertToDisplay, buttonText
                    )

                    self._connectButtonClicked(  # type:ignore
                        button0, button0Slot)

    def _connectButtonClicked(self, button: Button, slot) -> None:
        button.clicked.connect(slot)

    def _configSpecialButton(self, button: Button):
        text = button.text()

        if text == "c":
            self._connectButtonClicked(button, self._clear)

        if text == "D":
            self._connectButtonClicked(button, self._backspace)

        if text == "N":
            self._connectButtonClicked(button, self._invertNumber)

        if text in "+-*/^%!":
            self._connectButtonClicked(
                button,
                self._makeSlot(self._configLeftOp, text)
            )

        if text == "sqrt":
            self._connectButtonClicked(
                button,
                self._makeSlot(self._configLeftOp, text)
            )

        if text == "=":
            self._connectButtonClicked(button, self._eq)

    def _insertToDisplay(self, text):
        newDisplayValue = self.display.text() + text

        if not isValidNumber(newDisplayValue):
            return

        self.display.insert(text)
        self.display.setFocus()

    @Slot()
    def _makeSlot(self, func, *args, **kwargs):
        @Slot(bool)
        def realSlot():
            func(*args, **kwargs)
        return realSlot

    @Slot()
    def _invertNumber(self):
        displayText = self.display.text()

        if not isValidNumber(displayText):
            return

        number = convertToNumber(displayText) * -1
        self.display.setText(str(number))

    @Slot()
    def _clear(self):
        self._leftNum = None
        self._operator = None
        self._rightNum = None
        self.equation = self._equationInitialValue
        self.display.clear()
        self.display.setFocus()

    @Slot()
    def _configLeftOp(self, text):
        displayText = self.display.text()  # meu numero _leftNum
        self.display.clear()
        self.display.setFocus()

        # Se a pessoa clicou no operador
        # sem configurar qualquer número
        if not isValidNumber(displayText) and self._leftNum is None:
            self._showErrorWithInfo("Você não digitou nada",
                                    "É necessário inserir algum número antes "
                                    "do operador")
            return

        # Se houver algo no número da esquerda,
        # Apenas aguardar o numero da direita e fazer a conversão
        if self._leftNum is None:
            self._leftNum = convertToNumber(displayText)

        self._operator = text

        if self._operator == "sqrt":
            if not self._leftNum < 0:  # type: ignore
                result = math.sqrt(self._leftNum)  # type: ignore
                self.equation = f"{self._operator} {self._leftNum} = {result}"
                self._leftNum = result
                self.info.setText(self.equation)
                self._rightNum = None
                self.display.setFocus()
                return

            else:
                self._showErrorWithInfo(
                    "Raiz negativa", "A raiz quadrada de um "
                    "número negativo é imaginária e por isso não "
                    "pode ser efetuada")
                self._clear()
                return
        elif self._operator == "!":
            result = math.factorial(self._leftNum)  # type: ignore
            # num!
            self.equation = f"{self._leftNum}{self._operator} = {result}"
            self.info.setText(self.equation)
            self._leftNum = result
            self._rightNum = None
            self.display.setFocus()

        else:
            self.equation = f"{self._leftNum} {self._operator} ??"

    @Slot()
    def _eq(self):
        displayText = self.display.text()

        if not isValidNumber(displayText) or self._leftNum is None:
            self._showErrorWithInfo(
                "Equação incompleta", "Digite outro número")
            return

        if self._operator == "sqrt" or self._operator == "!":
            self._rightNum = None

        elif self._operator == "%":
            if not self._leftNum < 0:  # type: ignore
                self._rightNum = convertToNumber(displayText)
                self.equation = f"({self._leftNum} * {self._rightNum})/100"
            else:
                self._showErrorWithInfo("Porcentagem negativa",
                                        "Insira um número "
                                        "válido para realizar a porcentagem")
                self._clear()

        else:
            self._rightNum = convertToNumber(displayText)
            self.equation = f"{self._leftNum} {self._operator} " \
                f"{self._rightNum}"

        result = "error"

        try:
            if "^" in self.equation and isinstance(
                    self._leftNum, (float, int)
            ) and self._rightNum is not None:
                result = math.pow(self._leftNum, self._rightNum)

            elif "!" in self.equation and isinstance(
                    self._leftNum, float | int) and self._rightNum is None:
                result = math.factorial(self._leftNum)  # type: ignore
                # num!
                self.equation = f"{self._leftNum}! = {result}"
            else:
                result = eval(self.equation)

        except ZeroDivisionError:
            self._showErrorWithInfo(
                "Divisão por zero", "Não é possível dividir por zero"
            )
        except OverflowError:
            self._showErrorWithInfo(
                "Número muito grande", "O resultado digitado excedeu "
                "o limite de memória disponível")

        self.display.clear()
        self.info.setText(f"{self.equation} = {result}")
        self._leftNum = result
        self._rightNum = None
        self.display.setFocus()

        if result == "error":
            self._leftNum = None

    @Slot()
    def _backspace(self):
        self.display.backspace()
        self.display.setFocus()

    def _showErrorWithInfo(self, text, informative_text):
        msgBox = self.window.makeMsgBox()
        msgBox.setText(text)
        msgBox.setInformativeText(informative_text)
        msgBox.setIcon(msgBox.Icon.Warning)

        msgBox.setStandardButtons(
            msgBox.StandardButton.Ok |
            msgBox.StandardButton.Cancel
        )
        msgBox.exec()
        self.display.setFocus()

        # Trocando o texto do botão de texto
        # msgBox.button(msgBox.StandardButton.Ok).setText("Entendido")

        # Como saber qual botão o usuário clicou?
        # result = msgBox.exec()
        # if result == msgBox.StandardButton.Ok:
        #     print("clicou no Ok")

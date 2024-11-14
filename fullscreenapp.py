import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QPalette

class LoadingBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Definir cor de fundo da barra
        self.setStyleSheet("background-color: black; border: 2px solid yellow;")
        
        # Criar a parte animada da barra de carregamento
        self.loading_bar = QFrame(self)
        self.loading_bar.setStyleSheet("background-color: yellow;")
        self.loading_bar.setGeometry(0, 0, 0, 10)  # Inicialmente com largura 0
        
        # Animação para a barra de carregamento
        self.animation = QPropertyAnimation(self.loading_bar, b"geometry")
        self.animation.setDuration(2000)  # Tempo de duração de cada ciclo
        self.animation.setStartValue(QRect(0, 0, 0, 10))  # Começa com largura 0
        self.animation.setEndValue(QRect(0, 0, 1000, 10))  # Vai até o fim da largura
        self.animation.setLoopCount(-1)  # Loop infinito
        self.animation.setEasingCurve(QEasingCurve.Linear)  # Movimento suave
        self.animation.start()

    def resizeEvent(self, event):
        # Ajustar a largura da barra conforme a largura do widget pai
        self.loading_bar.setGeometry(0, self.height() - 60, self.width(), 10)


class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Usando showFullScreen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()  # Coloca a janela em fullscreen

        # Cor de fundo preta
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor('black'))
        self.setPalette(palette)

        # Configuração de fontes mais parecidas com medieval
        fonte_medieval = QFont('MedievalSharp', 60, QFont.Bold)
        subtitulo_fonte = QFont('MedievalSharp', 40, QFont.Bold)  # Fonte medieval ajustada para subtítulo

        # Título
        self.titulo = QLabel("Orgãos Lopes", self)
        self.titulo.setFont(fonte_medieval)
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet("color: white")  # Mudando a cor para branco

        # Subtítulo
        self.subtitulo = QLabel("Dulce Cecilia", self)
        self.subtitulo.setFont(subtitulo_fonte)
        self.subtitulo.setAlignment(Qt.AlignCenter)
        self.subtitulo.setStyleSheet("color: white")  # Mudando a cor para branco

        # Layout para o título e subtítulo
        layout = QVBoxLayout(self)
        layout.addWidget(self.titulo)
        layout.addWidget(self.subtitulo)
        layout.setAlignment(Qt.AlignCenter)  # Centraliza os itens dentro do layout

        # Barra de Carregamento na parte inferior
        self.loading_bar = LoadingBar(self)
        layout.addWidget(self.loading_bar)

        # Ajustar o layout para ocupar toda a janela
        self.setLayout(layout)

        # Texto "Carregando" com animação dos pontos
        self.carregando = QLabel("Carregando", self)
        self.carregando.setFont(QFont('Arial', 30, QFont.Bold))
        self.carregando.setAlignment(Qt.AlignLeft)
        self.carregando.setStyleSheet("color: white")  # Mudando a cor para branco
        self.carregando.setGeometry(30, self.height() - 60, 200, 50)  # Posiciona no canto inferior esquerdo

        # Animação para o texto "Carregando" (pontos)
        self.dots = 0
        self.carregando_timer = QTimer(self)
        self.carregando_timer.timeout.connect(self.updateCarregando)
        self.carregando_timer.start(500)  # Atualiza a cada 500ms

        # Exibir a janela
        self.show()

        # Iniciar o temporizador de fechamento após 10 segundos
        QTimer.singleShot(10000, self.close)  # Fechar após 10 segundos

    def updateCarregando(self):
        # Atualiza o texto "Carregando" com os pontos
        if self.dots == 3:
            self.dots = 0
            self.carregando.setText("Carregando")
        else:
            self.carregando.setText("Carregando" + "." * (self.dots + 1))
            self.dots += 1


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Melhorar a aparência da aplicação
    tela_carregamento = LoadingScreen()
    tela_carregamento.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

#include "pseudogen.hpp"
#include <QWidget>
#include <QtCore/QFile>
#include <QtCore/QTextStream>
#include <QtCore/QUrl>
#include <QtGui/QDesktopServices>
#include <QtGui/QFont>
#include <QtWidgets/QApplication>
#include <QtWidgets/QFileDialog>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMessageBox>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QTextEdit>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

class MainWindow : public QMainWindow {
  Q_OBJECT

private:
  QLineEdit *inputFileEdit;
  QLineEdit *pgenFileEdit;
  QLineEdit *outputFileEdit;
  QTextEdit *previewEdit;
  QPushButton *runButton;
  QPushButton *browseInputButton;
  QPushButton *browsePgenButton;
  QPushButton *browseOutputButton;
  QPushButton *openOutputButton;
  QStatusBar *statusBar;

private slots:
  void browseInputFile() {
    QString fileName = QFileDialog::getOpenFileName(
        this, "Выберите входной файл", "",
        "C++ Files (*.cpp *.c *.h *.hpp);;All Files (*)");
    if (!fileName.isEmpty()) {
      inputFileEdit->setText(fileName);
      updatePreview();
    }
  }

  void browsePgenFile() {
    QString fileName =
        QFileDialog::getOpenFileName(this, "Выберите файл правил (*.pgen)", "",
                                     "PGEN Files (*.pgen);;All Files (*)");
    if (!fileName.isEmpty()) {
      pgenFileEdit->setText(fileName);
    }
  }

  void browseOutputFile() {
    QString fileName =
        QFileDialog::getSaveFileName(this, "Сохранить результат как", "",
                                     "Text Files (*.txt);;All Files (*)");
    if (!fileName.isEmpty()) {
      outputFileEdit->setText(fileName);
    }
  }

  void openOutputFile() {
    QString outputFile = outputFileEdit->text();
    if (outputFile.isEmpty()) {
      QMessageBox::warning(this, "Предупреждение",
                           "Сначала укажите выходной файл");
      return;
    }

    QFile file(outputFile);
    if (file.exists()) {
      QDesktopServices::openUrl(QUrl::fromLocalFile(outputFile));
    } else {
      QMessageBox::warning(this, "Ошибка", "Выходной файл еще не создан");
    }
  }

  void updatePreview() {
    QString inputFile = inputFileEdit->text();
    if (inputFile.isEmpty())
      return;

    QFile file(inputFile);
    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
      QTextStream stream(&file);
      previewEdit->setPlainText(stream.readAll());
      file.close();
    }
  }

  void runProcessing() {
    // Проверка входных данных
    if (inputFileEdit->text().isEmpty()) {
      QMessageBox::warning(this, "Ошибка", "Укажите входной файл");
      return;
    }

    if (pgenFileEdit->text().isEmpty()) {
      QMessageBox::warning(this, "Ошибка", "Укажите файл правил (.pgen)");
      return;
    }

    if (outputFileEdit->text().isEmpty()) {
      QMessageBox::warning(this, "Ошибка", "Укажите выходной файл");
      return;
    }

    // Запуск обработки
    try {
      PseudoGen pg;
      pg.input = inputFileEdit->text().toStdString();
      pg.pgen = pgenFileEdit->text().toStdString();
      pg.output = outputFileEdit->text().toStdString();

      statusBar->showMessage("Генерация псевдокода...");

      pg.pseudocode();

      statusBar->showMessage("Псевдокод успешно создан", 3000);

      QMessageBox::information(this, "Успех",
                               "Псевдокод создан успешно!\n"
                               "Входной файл: " +
                                   inputFileEdit->text() +
                                   "\n"
                                   "Выходной файл: " +
                                   outputFileEdit->text());

    } catch (const std::exception &e) {
      QMessageBox::critical(this, "Ошибка",
                            QString("Произошла ошибка: ") + e.what());
      statusBar->showMessage("Ошибка обработки", 3000);
    }
  }

public:
  MainWindow(QWidget *parent = nullptr) : QMainWindow(parent) {
    setWindowTitle("PseudoGen GUI - Генератор псевдокода");
    setMinimumSize(800, 600);

    // Центральный виджет
    QWidget *centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);

    // Основной layout
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

    // Группа ввода файлов
    QGroupBox *inputGroup = new QGroupBox("Входные данные", this);
    QGridLayout *inputLayout = new QGridLayout(inputGroup);

    // Входной файл (исходный код)
    inputLayout->addWidget(new QLabel("Исходный код:"), 0, 0);
    inputFileEdit = new QLineEdit(this);
    inputFileEdit->setReadOnly(true);
    inputFileEdit->setPlaceholderText("Выберите файл с исходным кодом...");
    inputLayout->addWidget(inputFileEdit, 0, 1);
    browseInputButton = new QPushButton("Обзор...", this);
    connect(browseInputButton, &QPushButton::clicked, this,
            &MainWindow::browseInputFile);
    inputLayout->addWidget(browseInputButton, 0, 2);

    // Файл правил (.pgen)
    inputLayout->addWidget(new QLabel("Файл правил:"), 1, 0);
    pgenFileEdit = new QLineEdit(this);
    pgenFileEdit->setReadOnly(true);
    pgenFileEdit->setPlaceholderText("Выберите файл с правилами (*.pgen)...");
    inputLayout->addWidget(pgenFileEdit, 1, 1);
    browsePgenButton = new QPushButton("Обзор...", this);
    connect(browsePgenButton, &QPushButton::clicked, this,
            &MainWindow::browsePgenFile);
    inputLayout->addWidget(browsePgenButton, 1, 2);

    // Выходной файл
    inputLayout->addWidget(new QLabel("Выходной файл:"), 2, 0);
    outputFileEdit = new QLineEdit(this);
    outputFileEdit->setReadOnly(true);
    outputFileEdit->setPlaceholderText("Куда сохранить результат...");
    inputLayout->addWidget(outputFileEdit, 2, 1);

    QHBoxLayout *outputButtonsLayout = new QHBoxLayout();
    browseOutputButton = new QPushButton("Обзор...", this);
    connect(browseOutputButton, &QPushButton::clicked, this,
            &MainWindow::browseOutputFile);
    outputButtonsLayout->addWidget(browseOutputButton);

    openOutputButton = new QPushButton("Открыть результат", this);
    connect(openOutputButton, &QPushButton::clicked, this,
            &MainWindow::openOutputFile);
    outputButtonsLayout->addWidget(openOutputButton);

    inputLayout->addLayout(outputButtonsLayout, 2, 2);

    mainLayout->addWidget(inputGroup);

    // Кнопка выполнения
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    buttonLayout->addStretch();

    runButton = new QPushButton("Сгенерировать псевдокод", this);
    runButton->setMinimumHeight(40);
    runButton->setStyleSheet("QPushButton {"
                             "   background-color: #4CAF50;"
                             "   color: white;"
                             "   padding: 8px 16px;"
                             "   font-weight: bold;"
                             "   font-size: 14px;"
                             "   border-radius: 4px;"
                             "}"
                             "QPushButton:hover {"
                             "   background-color: #45a049;"
                             "}"
                             "QPushButton:pressed {"
                             "   background-color: #3d8b40;"
                             "}");
    connect(runButton, &QPushButton::clicked, this, &MainWindow::runProcessing);
    buttonLayout->addWidget(runButton);

    buttonLayout->addStretch();
    mainLayout->addLayout(buttonLayout);

    // Превью входного файла
    QGroupBox *previewGroup = new QGroupBox("Превью исходного кода", this);
    QVBoxLayout *previewLayout = new QVBoxLayout(previewGroup);

    previewEdit = new QTextEdit(this);
    previewEdit->setReadOnly(true);
    previewEdit->setFont(QFont("Courier New", 10));
    previewLayout->addWidget(previewEdit);

    mainLayout->addWidget(previewGroup);

    // Статус бар
    statusBar = statusBar();
    statusBar->showMessage("Готов");
  }
};

int main(int argc, char *argv[]) {
  QApplication app(argc, argv);

  app.setApplicationName("PseudoGen");
  app.setApplicationVersion("1.0");
  app.setOrganizationName("PseudoGen");

  MainWindow window;
  window.show();

  return app.exec();
}

#include "gui.moc"

#include <QApplication>
#include <QMainWindow>
#include <QTabWidget>
#include <QLabel>
#include <QFrame>
#include <QPushButton>
#include <QProgressBar>
#include <QSplashScreen>
#include <QGraphicsColorizeEffect>
#include <QVBoxLayout>
#include <QMessageBox>
#include <QFont>
#include <QScreen>
#include <QPixmap>
#include <QCoreApplication>
#include <QTcpSocket>
#include <QDebug>
#include <QTime>

#include "data_engine.h"  // Include your data_engine header

constexpr int nbr_SV_engine = 12;
const QString address = "192.168.0.149";  // IP Address
const int port = 12345;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    void setupUi();
    void tab1();
    void sendData(const QString &text);
    void endProgram();

    QTabWidget *tabWidget;
    QVector<QFrame*> SV_frame_engine;
    QVector<QLabel*> SV_frame_engine_status;
    QVector<QLabel*> SV_frame_engine_label;
    QVector<QPushButton*> SV_button_open_engine;
    QVector<QPushButton*> SV_button_close_engine;
    QPixmap backgroundPixmap;

    bool uC_connection = false;
};

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setupUi();
}

MainWindow::~MainWindow() {}

void MainWindow::setupUi() {
    this->resize(1922, 1237);
    this->setWindowFlags(this->windowFlags() & ~Qt::WindowCloseButtonHint);
    this->setStyleSheet("background-color: rgb(236,236,236)");

    tabWidget = new QTabWidget(this);
    tabWidget->setGeometry(0, 0, 2000, 1080);
    tabWidget->setStyleSheet("QTabBar::tab { height: 40px; width: 150px; }");

    QStringList tabNames = {"Engine cycle", "Cooling cycle", "Test", "Plot", "Options"};
    for (const auto &name : tabNames) {
        tabWidget->addTab(new QWidget(), name);
    }

    tab1();
}

void MainWindow::tab1() {
    // Set up background picture (PID_Engine)
    backgroundPixmap.load("Synoptique_Arrax_Engine.png");
    QLabel *backgroundEngine = new QLabel(this);
    backgroundEngine->setGeometry(-30, 50, 2100, 900);
    backgroundEngine->setPixmap(backgroundPixmap);

    // Dimensions of the control objects
    int width1 = 111, width2 = 55, width3 = 41, height1 = 91, height2 = 16, height3 = 28;

    // Create control objects
    for (int i = 0; i < nbr_SV_engine; ++i) {
        SV_frame_engine.append(new QFrame(this));
        SV_frame_engine_status.append(new QLabel(this));
        SV_frame_engine_label.append(new QLabel(this));
        SV_button_open_engine.append(new QPushButton(this));
        SV_button_close_engine.append(new QPushButton(this));
    }

    // Setting up control objects based on engine_object data
    for (int i = 0; i < nbr_SV_engine; ++i) {
        QString valveName = engine_object.keys().at(i);
        auto attributes = engine_object[valveName];

        auto frame = SV_frame_engine[i];
        auto labelStatus = SV_frame_engine_status[i];
        auto labelEngine = SV_frame_engine_label[i];
        auto openButton = SV_button_open_engine[i];
        auto closeButton = SV_button_close_engine[i];

        // Set geometries based on attributes
        frame->setGeometry(QRect(attributes["frame_dim"].toPoint(), QSize(width1, height1)));
        labelStatus->setGeometry(QRect(attributes["status_dim"].toPoint(), QSize(width1, height2)));
        labelEngine->setGeometry(QRect(attributes["label_dim"].toPoint(), QSize(width2, height2)));
        openButton->setGeometry(QRect(attributes["ouvert_button_dim"].toPoint(), QSize(width3, height3)));
        closeButton->setGeometry(QRect(attributes["ferme_button_dim"].toPoint(), QSize(width3 + 7, height3)));

        // Set fonts
        QFont font("Arial", 8, QFont::Bold);
        labelEngine->setFont(font);
        labelStatus->setFont(font);
        openButton->setFont(font);
        closeButton->setFont(font);

        // Set label and styles for widgets
        QString status = "Open";
        labelEngine->setText(QString("<u>%1 status:</u>").arg(valveName));
        labelStatus->setText(status);
        auto colorEffect = new QGraphicsColorizeEffect();
        colorEffect->setColor(Qt::darkGreen);
        labelStatus->setGraphicsEffect(colorEffect);

        // Set styles for the widgets
        frame->setStyleSheet("QFrame, QLabel, QToolTip { background-color: rgb(230, 230, 230); border: 3px solid grey; border-radius: 10px; padding: 2px; }");

        // Set text and style for open and close buttons
        openButton->setText("Open");
        openButton->setStyleSheet("QPushButton { border: 1px solid black; background-color: white; border-radius: 3px; height: 30px; }"
                                   "QPushButton:hover { background-color: #ADADAD; border: 2px rgb(255,200,200); }");

        closeButton->setText("Close");
        closeButton->setStyleSheet("QPushButton { border: 1px solid black; background-color: white; border-radius: 3px; height: 30px; }"
                                    "QPushButton:hover { background-color: #ADADAD; border: 2px rgb(255,200,200); }");
    }
}

void MainWindow::sendData(const QString &text) {
    QTcpSocket clientSocket;
    clientSocket.connectToHost(address, port);
    clientSocket.write(text.toUtf8());
    clientSocket.flush();
    clientSocket.waitForBytesWritten();
    clientSocket.disconnectFromHost();
}

void MainWindow::endProgram() {
    QMessageBox msgBox;
    msgBox.setIcon(QMessageBox::Warning);
    msgBox.setText("Are you sure to quit?");
    msgBox.setStandardButtons(QMessageBox::Yes | QMessageBox::No);
    
    if (msgBox.exec() == QMessageBox::Yes) {
        qDebug() << "\n\n\nYou closed the program.\nDid it work? (ง'-̀'́)ง  Ϟ  ฝ('-'ฝ)\n\n\n";
        QCoreApplication::quit();
    }
}

class SplashScreen : public QSplashScreen {
public:
    SplashScreen(const QPixmap &pixmap);
    void updateProgress(int value);

private:
    QProgressBar *progressBar;
    QLabel *percentLabel;
};

SplashScreen::SplashScreen(const QPixmap &pixmap) : QSplashScreen(pixmap) {
    setWindowFlag(Qt::FramelessWindowHint);
    setWindowFlag(Qt::WindowStaysOnTopHint);
    setStyleSheet("background-color: white;");

    progressBar = new QProgressBar(this);
    progressBar->setGeometry(10, pixmap.height() + 10, pixmap.width() - 20, 20);
    progressBar->setRange(0, 100);
    progressBar->setStyleSheet("QProgressBar { border: 2px solid #555; border-radius: 5px; text-align: center; }"
                               "QProgressBar::chunk { background: #1a75ff; width: 20px; height: 20px; }");

    percentLabel = new QLabel("0%", this);
    percentLabel->setFont(QFont("Arial", 16));
    percentLabel->setAlignment(Qt::AlignCenter);
}

void SplashScreen::updateProgress(int value) {
    progressBar->setValue(value);
    percentLabel->setText(QString("%1%").arg(value));
}

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    QPixmap splashPixmap("Logo_Arrax.png");
    SplashScreen splash(splashPixmap);

    QScreen *screen = app.primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - splashPixmap.width()) / 2;
    int y = (screenGeometry.height() - splashPixmap.height()) / 2;
    splash.move(x, y);

    splash.show();

    for (int i = 1; i <= 100; ++i) {
        QThread::msleep(10);  // Adjust the sleep time as needed
        splash.updateProgress(i);
        app.processEvents();
    }

    MainWindow mainWindow;
    splash.finish(&mainWindow);
    mainWindow.showFullScreen();

    return app.exec();
}

#include "moc_yourfilename.cpp"  // Include the MOC generated file for signal-slot functionality

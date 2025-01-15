/*
HMI for 1kN rocket engine
Creator: Mehdi Delouane

EP --> End Program
uC --> Microcontroller
P&ID --> Piping & Instrumentation Drawing
RSUT --> Register-Sum Up Table
*/

// Import libraries
#include <QApplication>
#include <QMainWindow>
#include <QTabWidget>
#include <QLabel>
#include <QPixmap>
#include <QWidget>
#include <QVBoxLayout>
#include <QPushButton>
#include <QProgressBar>
#include <QTimer>
#include <QFont>
#include <QTableWidget>
#include <QHeaderView>
#include <QMap>
#include <QDateTime>
#include <QSpinBox>
#include <QPainter>
#include <QUdpSocket>
#include <QMessageBox>
#include "chrono.h"
#include "valve.h"
#include "engine_cycle.h"


// Cooling tab
QWidget* createTab2(QWidget* parent) {
    QWidget* tab2 = new QWidget(parent);

    // Add the image label
    QLabel* imageLabel = new QLabel(tab2);
    QPixmap pixmap("C:/Python_Project/IPL/IHM_cpp/Arrax_Cooling.png");
    imageLabel->setPixmap(pixmap);
    imageLabel->setScaledContents(true);
    imageLabel->setGeometry(0, 0, 1535, 750);

    // Add the logo label
    QLabel* LogoLabel = new QLabel(tab2);
    QPixmap pixmap_logo("C:/Python_Project/IPL/IHM_cpp/Logo_IPL.png");
    LogoLabel->setPixmap(pixmap_logo);
    LogoLabel->setScaledContents(true);
    LogoLabel->setGeometry(1280, 50, 200, 80);

    // Close button for tab1
    QPushButton* closeButton1 = new QPushButton("End program", tab2);
    closeButton1->setGeometry(1350, 690, 120, 40);
    closeButton1->setStyleSheet(R"(
        QPushButton {
            border: 2px solid #B20000;
            background-color: #FF1400;
            border-radius: 3px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: rgb(255,100,100);
            border: 2px solid rgb(255,200,200);
        }
    )");
    closeButton1->setFont(QFont("Arial", 10, QFont::Bold));
    QObject::connect(closeButton1, &QPushButton::clicked, parent, &QWidget::close);

    QTableWidget* table = new QTableWidget(0, 2, tab2); // Start with 0 rows, as we'll add rows dynamically
    table->setGeometry(200, 420, 220, 170);
    table->setHorizontalHeaderLabels({"Valve Name", "Status"});
    QFont font = table->horizontalHeader()->font();
    font.setBold(true);
    table->horizontalHeader()->setFont(font);
    table->verticalHeader()->setVisible(false);
    table->setColumnWidth(0, 120);
    table->setColumnWidth(1, 100);
    table->verticalHeader()->setDefaultSectionSize(10);
    table->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);  // Remove vertical scrollbar
    table->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);    // Remove horizontal scrollbar
    table->setStyleSheet("QTableWidget { border: 2px solid black;background-color: #ededed; }""QHeaderView::section { "
                         "background-color: #dbdbdb; }");

    createValve(tab2, "SV51", QPoint(310, 195), "Close", table);
    createValve(tab2, "SV52", QPoint(465, 450), "Close", table);
    createValve(tab2, "SV53", QPoint(465, 190), "Open", table);
    createValve(tab2, "SV61", QPoint(752, 518), "Open", table);
    createValve(tab2, "SV62", QPoint(752, 120), "Open", table);
    createValve(tab2, "SV63", QPoint(904, 227), "Open", table);

    table->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    table->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    chrono(tab2);
    return tab2;
}

// Test tab
QWidget* createTab3(QWidget* parent) {
    QWidget* tab3 = new QWidget(parent);

    QString spinBoxStyle = R"(
        QDoubleSpinBox {
            border: 2px solid #5A5A5A;  /* Border color */
            border-radius: 5px;         /* Rounded corners */
            padding: 5px;               /* Padding inside the box */
            background: #F0F0F0;        /* Background color */
            color: #333333;             /* Text color */
            font-size: 16px;            /* Font size */
        }
        /* Style the up and down buttons */
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            width: 25px;                  /* Button width */
            background-color: #CCCCCC;    /* Button background */
            border: 1px solid #333333;    /* Button border color */
            border-radius: 1px;           /* Rounded corners for button frame */
        }
        /* Style the up button */
        QDoubleSpinBox::up-button {
            width: 20px; /* Width of the up button */
            height: 10px; /* Height of the up button */
            subcontrol-origin: border;
            subcontrol-position: top right;
        }

        /* Style the down button */
        QDoubleSpinBox::down-button {
            width: 20px; /* Width of the down button */
            height: 10px; /* Height of the down button */
            subcontrol-origin: border;
            subcontrol-position: bottom right;
        }
    )";

    // Title label
    QLabel* titleLabel = new QLabel("Tank pressure control", tab3);
    titleLabel->setGeometry(100, 20, 200, 30);
    titleLabel->setAlignment(Qt::AlignCenter);
    titleLabel->setFont(QFont("Arial", 12, QFont::Bold));

    // LOX Pressure Label and DoubleSpinBox
    QLabel* loxLabel = new QLabel("LOX pressure", tab3);
    loxLabel->setGeometry(60, 60, 100, 20);
    loxLabel->setFont(QFont("Arial", 10));
    QDoubleSpinBox* loxSpinBox = new QDoubleSpinBox(tab3);
    loxSpinBox->setGeometry(60, 90, 100, 30);
    loxSpinBox->setStyleSheet(spinBoxStyle);
    loxSpinBox->setDecimals(2); // Allow up to 2 decimal places
    loxSpinBox->setValue(16.00); // Default value

    // ETH Pressure Label and DoubleSpinBox
    QLabel* ethLabel = new QLabel("ETH pressure", tab3);
    ethLabel->setGeometry(170, 60, 100, 20);
    ethLabel->setFont(QFont("Arial", 10));
    QDoubleSpinBox* ethSpinBox = new QDoubleSpinBox(tab3);
    ethSpinBox->setGeometry(170, 90, 100, 30);
    ethSpinBox->setStyleSheet(spinBoxStyle);
    ethSpinBox->setDecimals(2); // Allow up to 2 decimal places
    ethSpinBox->setValue(16.00); // Default value

    // H2O Pressure Label and DoubleSpinBox
    QLabel* h2oLabel = new QLabel("H2O pressure", tab3);
    h2oLabel->setGeometry(280, 60, 100, 20);
    h2oLabel->setFont(QFont("Arial", 10));
    QDoubleSpinBox* h2oSpinBox = new QDoubleSpinBox(tab3);
    h2oSpinBox->setGeometry(280, 90, 100, 30);
    h2oSpinBox->setStyleSheet(spinBoxStyle);
    h2oSpinBox->setDecimals(2); // Allow up to 2 decimal places
    h2oSpinBox->setValue(4.00); // Default value

    // LOX Tank
    QLabel* loxTank = new QLabel(tab3);
    loxTank->setGeometry(50, 150, 80, 120);
    loxTank->setStyleSheet("background-color: blue; border-radius: 40px;");

    // ETH Tank
    QLabel* ethTank = new QLabel(tab3);
    ethTank->setGeometry(160, 150, 80, 120);
    ethTank->setStyleSheet("background-color: red; border-radius: 40px;");

    // H2O Tank
    QLabel* h2oTank = new QLabel(tab3);
    h2oTank->setGeometry(270, 150, 80, 120);
    h2oTank->setStyleSheet("background-color: yellow; border-radius: 40px;");

    // End Program Button
    QPushButton* closeButton1 = new QPushButton("End program", tab3);
    closeButton1->setGeometry(1350, 690, 120, 40);
    closeButton1->setStyleSheet(R"(
        QPushButton {
            border: 2px solid #B20000;
            background-color: #FF1400;
            border-radius: 3px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: rgb(255,100,100);
            border: 2px solid rgb(255,200,200);
        }
    )");
    QObject::connect(closeButton1, &QPushButton::clicked, parent, &QWidget::close);

    return tab3;
}

// Function to create the fourth tab
QWidget* createTab4(QWidget* parent) {
    QWidget* tab4 = new QWidget(parent);

    QVBoxLayout* layout4 = new QVBoxLayout(tab4);
    QLabel* label4 = new QLabel("This is Tab 4");
    layout4->addWidget(label4);

    // Close button for tab4
    QPushButton* closeButton4 = new QPushButton("End program", tab4);
    closeButton4->setStyleSheet(R"(
        QPushButton {
            border: 2px solid #B20000;
            background-color: #FF1400;
            border-radius: 3px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: rgb(255,100,100);
            border: 2px solid rgb(255,200,200);
        }
    )");
    QObject::connect(closeButton4, &QPushButton::clicked, parent, &QWidget::close);
    layout4->addWidget(closeButton4);

    return tab4;
}

// Function to create the main window with tabs
QMainWindow* createMainWindow() {
    QMainWindow* mainWindow = new QMainWindow();

    // Set the window to be borderless and maximized (pseudo-fullscreen)
    mainWindow->setWindowFlags(Qt::FramelessWindowHint);
    mainWindow->showMaximized();

    // Create a QTabWidget to hold tabs
    QTabWidget* tabWidget = new QTabWidget(mainWindow);

    // Customize the tab widget's stylesheet
    tabWidget->setStyleSheet(R"(
    QTabWidget::pane { border: 1px solid #000000; }
    QTabBar::tab {
        background-color: #bcbaba; color: black; height: 40px; width: 150px; font-weight: bold;
        border: 1px solid #000000;
    }
    QTabBar::tab:hover { background-color: #a8a8a8; }
    QTabBar::tab:selected { background-color: #d4d4d4; }
)");

    // Add tabs to the main window
    tabWidget->addTab(createTab1(mainWindow), "Engine cycle");
    tabWidget->addTab(createTab2(mainWindow), "Cooling cycle");
    tabWidget->addTab(createTab3(mainWindow), "Test");
    tabWidget->addTab(createTab4(mainWindow), "Graphics");

    // Set the QTabWidget as the central widget of the main window
    mainWindow->setCentralWidget(tabWidget);

    return mainWindow;
}

// Function to create the loading screen with progress bar
QWidget* createLoadingScreen(QMainWindow* mainWindow) {
    QWidget* loadingScreen = new QWidget();
    loadingScreen->setWindowFlags(Qt::FramelessWindowHint | Qt::SplashScreen);
    loadingScreen->resize(300, 300);

    QVBoxLayout* layout = new QVBoxLayout(loadingScreen);

    // Image label
    QLabel* imageLabel = new QLabel();
    QPixmap pixmap("C:/Python_Project/IPL/IHM_cpp/Logo_Arrax.png");  // Update with your image path
    imageLabel->setPixmap(pixmap.scaled(300, 300, Qt::KeepAspectRatio, Qt::SmoothTransformation));
    layout->addWidget(imageLabel, 0, Qt::AlignCenter);

    // Progress bar
    QProgressBar* progressBar = new QProgressBar();
    progressBar->setRange(0, 100);
    progressBar->setValue(0);
    progressBar->setStyleSheet(R"(
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #1a75ff;
                width: 20px;
                height: 20px;
            }
)");
    layout->addWidget(progressBar);

    loadingScreen->setLayout(layout);

    // Timer to simulate loading progress
    QTimer* timer = new QTimer();
    QObject::connect(timer, &QTimer::timeout, [progressBar, timer, loadingScreen, mainWindow]() {
        int value = progressBar->value();
        if (value < 100) {
            progressBar->setValue(value + 2);  // Increase progress by 5%
        } else {
            timer->stop();
            loadingScreen->hide();
            mainWindow->show();
        }
    });

    timer->start(25);  // Update every 25ms

    return loadingScreen;
}

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    // Create the main window with tabs
    QMainWindow* mainWindow = createMainWindow();
    mainWindow->hide();  // Initially hide the main window

    // Create and show the loading screen
    QWidget* loadingScreen = createLoadingScreen(mainWindow);
    loadingScreen->show();

    return app.exec();
}

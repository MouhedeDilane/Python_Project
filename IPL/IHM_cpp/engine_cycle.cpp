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


// Engine tab
QWidget* createTab1(QWidget* parent) {
    QWidget* tab1 = new QWidget(parent);

    // Add the engine P&ID image
    QLabel* imageLabel = new QLabel(tab1);
    QPixmap pixmap("C:/Python_Project/IPL/IHM_cpp/Arrax_Engine.png");
    imageLabel->setPixmap(pixmap);
    imageLabel->setScaledContents(true);
    imageLabel->setGeometry(0, 0, 1533, 767);

    // Add the IPL logo
    QLabel* LogoLabel = new QLabel(tab1);
    QPixmap pixmap_logo("C:/Python_Project/IPL/IHM_cpp/Logo_IPL.png");
    LogoLabel->setPixmap(pixmap_logo);
    LogoLabel->setScaledContents(true);
    LogoLabel->setGeometry(1280, 50, 200, 80);

    // EP button for tab1
    QPushButton* closeButton1 = new QPushButton("End program", tab1);
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

    // Create the RSUT of tab1
    QTableWidget* table = new QTableWidget(0, 2, tab1);
    table->setGeometry(150, 400, 220, 315);
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

    // Create and position each valve and register it into the RSUT
    createValve(tab1, "SV11", QPoint(715, 523), "Open",table);
    createValve(tab1, "SV12", QPoint(1010, 435), "Open",table);
    createValve(tab1, "SV13", QPoint(1012, 578), "Open",table);
    createValve(tab1, "SV21", QPoint(712, 117), "Open",table);
    createValve(tab1, "SV22", QPoint(975, 205), "Open",table);
    createValve(tab1, "SV24", QPoint(1012, 60), "Open",table);
    createValve(tab1, "SV31", QPoint(110, 237), "Open",table);
    createValve(tab1, "SV32", QPoint(322, 210), "Open",table);
    createValve(tab1, "SV33", QPoint(519, 200), "Open",table);
    createValve(tab1, "SV34", QPoint(519, 435), "Open",table);
    createValve(tab1, "SV35", QPoint(1260, 159), "Open",table);
    createValve(tab1, "SV36", QPoint(1260, 480), "Open",table);
    chrono(tab1);
    return tab1;
}

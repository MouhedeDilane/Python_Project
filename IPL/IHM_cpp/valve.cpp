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
#include "valve.h"
#include "UDP.h"

// Map to store valves with their names as keys
QMap<QString, Valve> valveMap;

// Create, place valve object & connect it to sendCommand
Valve createValve(QWidget* parent, const QString& name, const QPoint& position, const QString& initialStatus, QTableWidget* table) {
    Valve valve;

    // Valve frame & design
    valve.frame = new QFrame(parent);
    valve.frame->setGeometry(position.x(), position.y(), 105, 85);
    valve.frame->setObjectName("valveFrame");
    valve.frame->setStyleSheet(R"(
        QFrame#valveFrame {
            background-color: rgb(230, 230, 230);
            border: 3px solid grey;
            border-radius: 10px;
            padding: 2px;
        }
    )");

    // Open and close buttons & design
    valve.openButton = new QPushButton("Open", valve.frame);
    valve.openButton->setGeometry(10, 50, 40, 25);
    valve.openButton->setFont(QFont("Arial", 8, QFont::Bold));
    valve.openButton->setStyleSheet(R"(
        QPushButton {
            border: 1px solid black;
            background-color: white;
            border-radius: 3px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: #ADADAD;
            border: 2px rgb(255,200,200);
        }
    )");

    valve.closeButton = new QPushButton("Close", valve.frame);
    valve.closeButton->setGeometry(55, 50, 40, 25);
    valve.closeButton->setFont(QFont("Arial", 8, QFont::Bold));
    valve.closeButton->setStyleSheet(R"(
        QPushButton {
            border: 1px solid black;
            background-color: white;
            border-radius: 3px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: #ADADAD;
            border: 2px rgb(255,200,200);
        }
    )");

    // Label for valve name
    valve.label = new QLabel(name + " status:", valve.frame);
    valve.label->setGeometry(15, 10, 70, 16);
    QFont font("Arial", 8, QFont::Bold);
    font.setUnderline(true);
    valve.label->setFont(font);
    valve.label->setStyleSheet("QLabel { color: black; }");

    // Label for valve status
    valve.statusLabel = new QLabel(initialStatus, valve.frame);
    valve.statusLabel->setGeometry(35, 26, 70, 16);
    valve.statusLabel->setFont(QFont("Arial", 8, QFont::Bold));
    valve.statusLabel->setStyleSheet(initialStatus == "Open" ? "QLabel { color: green; }" : "QLabel { color: red; }");

    // Add valve to the RSUT and save the row index
    int row = table->rowCount();
    table->insertRow(row);
    QTableWidgetItem* nameItem = new QTableWidgetItem(name);
    QTableWidgetItem* stateItem = new QTableWidgetItem(initialStatus);
    QFont font1("Arial", 8, QFont::Bold);
    nameItem->setTextAlignment(Qt::AlignCenter);
    nameItem->setFont(font1);
    nameItem->setForeground(QColor("black"));
    stateItem->setTextAlignment(Qt::AlignCenter);
    stateItem->setFont(font1);
    stateItem->setForeground(initialStatus == "Open" ? QColor("green") : QColor("red"));
    table->setItem(row, 0, nameItem);
    table->setItem(row, 1, stateItem);

    valve.tableRow = row;

    // Connect buttons to sendCommand
    QObject::connect(valve.openButton, &QPushButton::clicked, [=]() { sendCommand(valve, true, table); });
    QObject::connect(valve.closeButton, &QPushButton::clicked, [=]() { sendCommand(valve, false, table); });

    // Register valve into the QMap
    valveMap[name] = valve;
    return valve;
}


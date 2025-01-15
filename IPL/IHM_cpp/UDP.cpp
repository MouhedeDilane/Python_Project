// Import libraries
#include <QApplication>
#include <QTableWidget>
#include <QLabel>
#include <QMessageBox>
#include <QTimer>
#include <QColor>
#include <QElapsedTimer>
#include <QUdpSocket>
#include "valve.h"

// Configuration for UDP
const quint16 PORT = 5190;
const QString BROADCAST_IP = "192.168.0.100";  // Broadcast address
QUdpSocket *udpSocket = new QUdpSocket();

// Function to send state over UDP
void sendUdpState(const QString& valveName, const QString& state) {
    QString stateMessage = valveName + " " + state;
    QByteArray data = stateMessage.toUtf8();
    QHostAddress broadcastAddress(BROADCAST_IP);

    if (udpSocket->writeDatagram(data, broadcastAddress, PORT) == -1) {
        QMessageBox::critical(nullptr, "Error", "Failed to send state: " + udpSocket->errorString());
    } else {
        //QMessageBox::information(nullptr, "State Sent", "State sent: " + stateMessage);
    }
}

// Add function to wait for ACK
bool waitForAck(int timeout = 3000) {
    QElapsedTimer timer;
    timer.start();

    while (timer.elapsed() < timeout) {
        // Process pending UDP datagrams
        if (udpSocket->hasPendingDatagrams()) {
            QByteArray datagram;
            datagram.resize(udpSocket->pendingDatagramSize());
            QHostAddress sender;
            quint16 senderPort;
            udpSocket->readDatagram(datagram.data(), datagram.size(), &sender, &senderPort);

            QString receivedMessage = QString::fromUtf8(datagram);
            if (receivedMessage == "ACK") {
                return true;
            }
        }

        // Allow the event loop to process other events
        QCoreApplication::processEvents(QEventLoop::AllEvents, 100);
    }

    return false; // Timeout
}

// Update sendCommand function
void sendCommand(Valve valve, bool open, QTableWidget* table) {
    // Check if the command actually changes the valve state
    if ((open && valve.statusLabel->text() == "Open") || (!open && valve.statusLabel->text() == "Close")) {
        return;
    }

    // Reference to the state item in the table
    QTableWidgetItem* stateItem = table->item(valve.tableRow, 1);

    // Send the state message over UDP
    QString desiredState = open ? "Open" : "Close";
    sendUdpState(valve.label->text(), desiredState);

    // Wait for acknowledgment
    if (!waitForAck()) {
        QMessageBox::critical(nullptr, "Error", "No ACK received for valve " + valve.label->text());
        return;
    }

    // Update status label and table entry if ACK received
    if (open) {
        valve.statusLabel->setText("Open");
        valve.statusLabel->setStyleSheet("QLabel { color: green; }");
        stateItem->setText("Open");
        stateItem->setForeground(QColor("green"));
    } else {
        valve.statusLabel->setText("Close");
        valve.statusLabel->setStyleSheet("QLabel { color: red; }");
        stateItem->setText("Close");
        stateItem->setForeground(QColor("red"));
    }

    // Set up a fade effect to highlight changed valve
    QColor startColor = QColor("#c7c7c7");
    QColor endColor = QColor("#ededed");
    int fadeDuration = 1000;
    int steps = 30;
    int interval = fadeDuration / steps;

    QTimer* fadeTimer = new QTimer();
    int currentStep = 0;

    QObject::connect(fadeTimer, &QTimer::timeout, [=]() mutable {
        // Calculate the color at the current step
        float ratio = static_cast<float>(currentStep) / steps;
        int red = startColor.red() + ratio * (endColor.red() - startColor.red());
        int green = startColor.green() + ratio * (endColor.green() - startColor.green());
        int blue = startColor.blue() + ratio * (endColor.blue() - startColor.blue());
        QColor currentColor(red, green, blue);

        // Apply the current background color
        stateItem->setBackground(currentColor);

        currentStep++;
        if (currentStep > steps) {
            fadeTimer->stop();
            fadeTimer->deleteLater();
        }
    });

    fadeTimer->start(interval);
}

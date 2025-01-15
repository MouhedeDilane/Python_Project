#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QUdpSocket>
#include <QMessageBox>

// Configuration
const quint16 PORT = 5190;               // Chat port
const QString BROADCAST_IP = "192.168.0.102";  // Broadcast address

class UdpSenderWidget : public QWidget {
    Q_OBJECT

public:
    UdpSenderWidget(QWidget *parent = nullptr)
        : QWidget(parent), udpSocket(new QUdpSocket(this)), labelState(false) {

        // Set up UI
        QVBoxLayout *layout = new QVBoxLayout(this);

        // Input message section
        QLabel *messageLabel = new QLabel("Enter your message:", this);
        layout->addWidget(messageLabel);

        messageInput = new QLineEdit(this);
        layout->addWidget(messageInput);

        QPushButton *sendMessageButton = new QPushButton("Send Message", this);
        layout->addWidget(sendMessageButton);

        connect(sendMessageButton, &QPushButton::clicked, this, &UdpSenderWidget::sendUdpMessage);

        // Toggle state section
        QPushButton *toggleButton = new QPushButton("Toggle State", this);
        layout->addWidget(toggleButton);

        stateLabel = new QLabel("OFF", this);  // Initial state is OFF
        layout->addWidget(stateLabel);

        connect(toggleButton, &QPushButton::clicked, this, &UdpSenderWidget::toggleState);
    }

private slots:
    void sendUdpMessage() {
        QString message = messageInput->text();
        if (message.isEmpty()) {
            QMessageBox::warning(this, "Warning", "Message cannot be empty!");
            return;
        }

        QByteArray data = message.toUtf8();
        QHostAddress broadcastAddress(BROADCAST_IP);

        if (udpSocket->writeDatagram(data, broadcastAddress, PORT) == -1) {
            QMessageBox::critical(this, "Error", "Failed to send message: " + udpSocket->errorString());
        } else {
            QMessageBox::information(this, "Success", "Message sent: " + message);
        }

        messageInput->clear();
    }

    void toggleState() {
        // Toggle label state between "ON" and "OFF"
        labelState = !labelState;
        stateLabel->setText(labelState ? "ON" : "OFF");

        // Dynamically read the valve name (for now, assume "SV11" is fetched from a variable or sensor)
        QString valveName = "SV11";  // This would normally be dynamically fetched from a sensor/device or configuration

        // Construct the state message: e.g., "SV11 ON" or "SV11 OFF"
        QString stateMessage = valveName + " " + (labelState ? "ON" : "OFF");

        // Send the state message over UDP
        QByteArray data = stateMessage.toUtf8();
        QHostAddress broadcastAddress(BROADCAST_IP);

        if (udpSocket->writeDatagram(data, broadcastAddress, PORT) == -1) {
            QMessageBox::critical(this, "Error", "Failed to send state: " + udpSocket->errorString());
        } else {
            QMessageBox::information(this, "State Sent", "State sent: " + stateMessage);
        }
    }

private:
    QLineEdit *messageInput;
    QLabel *stateLabel;
    QUdpSocket *udpSocket;
    bool labelState;  // Tracks the state of the label (ON/OFF)
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    UdpSenderWidget widget;
    widget.setWindowTitle("UDP Message Sender");
    widget.resize(300, 200);  // Adjusted window size for additional elements
    widget.show();

    return app.exec();
}

#include "main.moc"

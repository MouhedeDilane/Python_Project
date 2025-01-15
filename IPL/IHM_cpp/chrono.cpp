#include <QLabel>
#include <QWidget>
#include <QTimer>
#include <QDateTime>

void chrono(QWidget* parent) {
    // Create the date and time label
    QLabel* dateTimeLabel = new QLabel(parent);
    dateTimeLabel->setGeometry(20, 10, 250, 30);
    dateTimeLabel->setFont(QFont("Arial", 10, QFont::Bold));
    dateTimeLabel->setStyleSheet("QLabel { color: black; }");

    // Create the chrono label
    QLabel* chronoLabel = new QLabel(parent);
    chronoLabel->setGeometry(50, 50, 250, 30);
    chronoLabel->setFont(QFont("Arial", 10, QFont::Bold));
    chronoLabel->setStyleSheet("QLabel { color: black; }");

    // Store the launch time
    QDateTime launchTime = QDateTime::currentDateTime();

    // Create the timer with the parent to ensure proper ownership
    QTimer* timer = new QTimer(parent);

    QObject::connect(timer, &QTimer::timeout, [=]() {
        // Update current date and time
        QDateTime currentDateTime = QDateTime::currentDateTime();
        dateTimeLabel->setText("Date: " + currentDateTime.toString("yyyy/MM/dd") +
                               " Time: " + currentDateTime.toString("hh:mm:ss"));

        // Calculate elapsed time since launch
        qint64 elapsedSecs = launchTime.secsTo(currentDateTime);
        QTime elapsedTime(0, 0); // Start from 00:00:00
        elapsedTime = elapsedTime.addSecs(elapsedSecs);
        QString chronoString = "Chrono: " + elapsedTime.toString("hh:mm:ss");
        chronoLabel->setText(chronoString);
    });

    // Start the timer
    timer->start(100);  // Update every 1 second
}

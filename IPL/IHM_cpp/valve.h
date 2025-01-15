#ifndef VALVE_H
#define VALVE_H

#include <QFrame>
#include <QLabel>
#include <QPushButton>
#include <QTableWidget>

// Valve objects & id
struct Valve {
    QFrame* frame;
    QLabel* label;
    QLabel* statusLabel;
    QPushButton* openButton;
    QPushButton* closeButton;
    int tableRow;
};



Valve createValve(QWidget* parent, const QString& name, const QPoint& position, const QString& initialStatus, QTableWidget* table);

#endif // VALVE_H

#ifndef UDP_H
#define UDP_H

#include <QString>
#include <QTableWidget>
#include "valve.h"

void sendUdpState(const QString& valveName, const QString& state);
bool waitForAck(int timeout = 3000);
void sendCommand(Valve valve, bool open, QTableWidget* table);
#endif // UDP_H

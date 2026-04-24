#include <QApplication>
#include "mainwindow.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    app.setApplicationName("Parameter Editor");
    app.setOrganizationName("NPCAP");
    
    MainWindow window;
    window.show();
    
    return app.exec();
}

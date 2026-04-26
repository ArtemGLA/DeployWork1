#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QSlider>
#include <QLabel>
#include <QPushButton>
#include <QTimer>
#include <QGroupBox>
#include <cmath>

#include "pfd_widget.h"

class DemoWindow : public QMainWindow {
public:
    DemoWindow() : simulating(false) {
        setWindowTitle("PFD Demo");
        resize(800, 600);
        
        auto* central = new QWidget(this);
        setCentralWidget(central);
        
        auto* layout = new QHBoxLayout(central);
        
        // PFD Widget
        pfd = new PFDWidget();
        pfd->setMinimumSize(500, 400);
        layout->addWidget(pfd, 2);
        
        // Controls
        auto* controlsGroup = new QGroupBox("Controls");
        auto* controlsLayout = new QVBoxLayout(controlsGroup);
        
        // Roll slider
        controlsLayout->addWidget(new QLabel("Roll:"));
        auto* rollSlider = new QSlider(Qt::Horizontal);
        rollSlider->setRange(-180, 180);
        rollSlider->setValue(0);
        connect(rollSlider, &QSlider::valueChanged, pfd, &PFDWidget::setRoll);
        controlsLayout->addWidget(rollSlider);
        
        // Pitch slider
        controlsLayout->addWidget(new QLabel("Pitch:"));
        auto* pitchSlider = new QSlider(Qt::Horizontal);
        pitchSlider->setRange(-90, 90);
        pitchSlider->setValue(0);
        connect(pitchSlider, &QSlider::valueChanged, pfd, &PFDWidget::setPitch);
        controlsLayout->addWidget(pitchSlider);
        
        // Heading slider
        controlsLayout->addWidget(new QLabel("Heading:"));
        auto* headingSlider = new QSlider(Qt::Horizontal);
        headingSlider->setRange(0, 360);
        headingSlider->setValue(0);
        connect(headingSlider, &QSlider::valueChanged, pfd, &PFDWidget::setHeading);
        controlsLayout->addWidget(headingSlider);
        
        // Speed slider
        controlsLayout->addWidget(new QLabel("Airspeed:"));
        auto* speedSlider = new QSlider(Qt::Horizontal);
        speedSlider->setRange(0, 50);
        speedSlider->setValue(0);
        connect(speedSlider, &QSlider::valueChanged, pfd, &PFDWidget::setAirspeed);
        controlsLayout->addWidget(speedSlider);
        
        // Altitude slider
        controlsLayout->addWidget(new QLabel("Altitude:"));
        auto* altSlider = new QSlider(Qt::Horizontal);
        altSlider->setRange(0, 500);
        altSlider->setValue(0);
        connect(altSlider, &QSlider::valueChanged, pfd, &PFDWidget::setAltitude);
        controlsLayout->addWidget(altSlider);
        
        // Simulate button
        auto* simButton = new QPushButton("Start Simulation");
        connect(simButton, &QPushButton::clicked, [this, simButton]() {
            simulating = !simulating;
            simButton->setText(simulating ? "Stop Simulation" : "Start Simulation");
        });
        controlsLayout->addWidget(simButton);
        
        // Armed checkbox
        auto* armButton = new QPushButton("Toggle Armed");
        connect(armButton, &QPushButton::clicked, [this]() {
            pfd->setArmed(!pfd->armed());
        });
        controlsLayout->addWidget(armButton);
        
        controlsLayout->addStretch();
        
        layout->addWidget(controlsGroup, 1);
        
        // Simulation timer
        auto* timer = new QTimer(this);
        connect(timer, &QTimer::timeout, this, &DemoWindow::updateSimulation);
        timer->start(50);  // 20 Hz
    }
    
private:
    void updateSimulation() {
        if (!simulating) return;
        
        static double t = 0;
        t += 0.05;
        
        // Simulate gentle banking turn
        pfd->setRoll(15 * sin(t * 0.5));
        pfd->setPitch(5 * sin(t * 0.3));
        pfd->setHeading(fmod(pfd->heading() + 0.5, 360));
        pfd->setAirspeed(15 + 3 * sin(t * 0.2));
        pfd->setAltitude(100 + 20 * sin(t * 0.1));
    }
    
    PFDWidget* pfd;
    bool simulating;
};

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    
    DemoWindow window;
    window.show();
    
    return app.exec();
}

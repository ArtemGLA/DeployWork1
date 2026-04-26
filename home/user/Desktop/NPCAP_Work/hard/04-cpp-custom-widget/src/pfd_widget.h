#pragma once

#include <QWidget>
#include <QPainter>
#include <QTimer>

/**
 * Primary Flight Display Widget.
 * 
 * TODO: Реализуйте отрисовку PFD
 */
class PFDWidget : public QWidget {
    Q_OBJECT
    
    Q_PROPERTY(qreal roll READ roll WRITE setRoll NOTIFY rollChanged)
    Q_PROPERTY(qreal pitch READ pitch WRITE setPitch NOTIFY pitchChanged)
    Q_PROPERTY(qreal heading READ heading WRITE setHeading NOTIFY headingChanged)
    Q_PROPERTY(qreal airspeed READ airspeed WRITE setAirspeed NOTIFY airspeedChanged)
    Q_PROPERTY(qreal altitude READ altitude WRITE setAltitude NOTIFY altitudeChanged)
    Q_PROPERTY(qreal verticalSpeed READ verticalSpeed WRITE setVerticalSpeed)
    Q_PROPERTY(bool armed READ armed WRITE setArmed)
    Q_PROPERTY(QString mode READ mode WRITE setMode)
    Q_PROPERTY(int batteryPercent READ batteryPercent WRITE setBatteryPercent)
    
public:
    explicit PFDWidget(QWidget* parent = nullptr);
    
    // Getters
    qreal roll() const { return m_roll; }
    qreal pitch() const { return m_pitch; }
    qreal heading() const { return m_heading; }
    qreal airspeed() const { return m_airspeed; }
    qreal altitude() const { return m_altitude; }
    qreal verticalSpeed() const { return m_verticalSpeed; }
    bool armed() const { return m_armed; }
    QString mode() const { return m_mode; }
    int batteryPercent() const { return m_batteryPercent; }
    
    // Setters
    void setRoll(qreal value);
    void setPitch(qreal value);
    void setHeading(qreal value);
    void setAirspeed(qreal value);
    void setAltitude(qreal value);
    void setVerticalSpeed(qreal value);
    void setArmed(bool value);
    void setMode(const QString& value);
    void setBatteryPercent(int value);
    
signals:
    void rollChanged(qreal value);
    void pitchChanged(qreal value);
    void headingChanged(qreal value);
    void airspeedChanged(qreal value);
    void altitudeChanged(qreal value);
    
protected:
    void paintEvent(QPaintEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;
    
private:
    // Данные полёта
    qreal m_roll = 0;           // -180..180 градусов
    qreal m_pitch = 0;          // -90..90 градусов
    qreal m_heading = 0;        // 0..360 градусов
    qreal m_airspeed = 0;       // м/с
    qreal m_altitude = 0;       // м
    qreal m_verticalSpeed = 0;  // м/с
    bool m_armed = false;
    QString m_mode = "STABILIZE";
    int m_batteryPercent = 100;
    bool m_gpsOk = true;
    bool m_connected = true;
    
    // Размеры компонентов (вычисляются при resize)
    QRect m_attitudeRect;
    QRect m_speedRect;
    QRect m_altitudeRect;
    QRect m_headingRect;
    QRect m_statusRect;
    
    // Методы отрисовки
    void calculateLayout();
    void drawAttitudeIndicator(QPainter& painter);
    void drawSpeedTape(QPainter& painter);
    void drawAltitudeTape(QPainter& painter);
    void drawHeadingIndicator(QPainter& painter);
    void drawStatusBar(QPainter& painter);
    
    // Вспомогательные
    void drawSkyGround(QPainter& painter, const QRect& rect, qreal pitch, qreal roll);
    void drawPitchLadder(QPainter& painter, const QRect& rect, qreal pitch, qreal roll);
    void drawAircraftSymbol(QPainter& painter, const QPoint& center);
    void drawRollIndicator(QPainter& painter, const QPoint& center, int radius, qreal roll);
    void drawTape(QPainter& painter, const QRect& rect, qreal value, qreal pixelsPerUnit, bool leftSide);
};

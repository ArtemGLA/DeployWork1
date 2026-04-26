/**
 * PFDWidget - реализация Primary Flight Display.
 * 
 * TODO: Реализуйте методы отрисовки
 */

#include "pfd_widget.h"
#include <QPainterPath>
#include <QLinearGradient>
#include <QtMath>

// Цвета
static const QColor SKY_COLOR_TOP(135, 206, 235);      // Light sky blue
static const QColor SKY_COLOR_BOTTOM(70, 130, 180);    // Steel blue
static const QColor GROUND_COLOR_TOP(139, 69, 19);     // Saddle brown
static const QColor GROUND_COLOR_BOTTOM(210, 105, 30); // Chocolate
static const QColor LINE_COLOR(255, 255, 255);
static const QColor INDICATOR_COLOR(255, 255, 0);
static const QColor DANGER_COLOR(255, 0, 0);
static const QColor WARNING_COLOR(255, 165, 0);
static const QColor OK_COLOR(0, 255, 0);
static const QColor BACKGROUND_COLOR(20, 20, 20);


PFDWidget::PFDWidget(QWidget* parent)
    : QWidget(parent)
{
    setMinimumSize(400, 300);
    setAutoFillBackground(true);
    
    QPalette pal = palette();
    pal.setColor(QPalette::Window, BACKGROUND_COLOR);
    setPalette(pal);
}

void PFDWidget::setRoll(qreal value)
{
    if (qFuzzyCompare(m_roll, value)) return;
    m_roll = qBound(-180.0, value, 180.0);
    emit rollChanged(m_roll);
    update();
}

void PFDWidget::setPitch(qreal value)
{
    if (qFuzzyCompare(m_pitch, value)) return;
    m_pitch = qBound(-90.0, value, 90.0);
    emit pitchChanged(m_pitch);
    update();
}

void PFDWidget::setHeading(qreal value)
{
    if (qFuzzyCompare(m_heading, value)) return;
    m_heading = fmod(value + 360.0, 360.0);
    emit headingChanged(m_heading);
    update();
}

void PFDWidget::setAirspeed(qreal value)
{
    if (qFuzzyCompare(m_airspeed, value)) return;
    m_airspeed = qMax(0.0, value);
    emit airspeedChanged(m_airspeed);
    update();
}

void PFDWidget::setAltitude(qreal value)
{
    if (qFuzzyCompare(m_altitude, value)) return;
    m_altitude = value;
    emit altitudeChanged(m_altitude);
    update();
}

void PFDWidget::setVerticalSpeed(qreal value) { m_verticalSpeed = value; update(); }
void PFDWidget::setArmed(bool value) { m_armed = value; update(); }
void PFDWidget::setMode(const QString& value) { m_mode = value; update(); }
void PFDWidget::setBatteryPercent(int value) { m_batteryPercent = qBound(0, value, 100); update(); }

void PFDWidget::resizeEvent(QResizeEvent* event)
{
    QWidget::resizeEvent(event);
    calculateLayout();
}

void PFDWidget::calculateLayout()
{
    int w = width();
    int h = height();
    
    int statusHeight = 30;
    int headingHeight = 50;
    int tapeWidth = 60;
    
    m_statusRect = QRect(0, 0, w, statusHeight);
    m_headingRect = QRect(0, h - headingHeight, w, headingHeight);
    m_speedRect = QRect(0, statusHeight, tapeWidth, h - statusHeight - headingHeight);
    m_altitudeRect = QRect(w - tapeWidth, statusHeight, tapeWidth, h - statusHeight - headingHeight);
    m_attitudeRect = QRect(tapeWidth, statusHeight, w - 2 * tapeWidth, h - statusHeight - headingHeight);
}

void PFDWidget::paintEvent(QPaintEvent* event)
{
    Q_UNUSED(event);
    
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    
    drawStatusBar(painter);
    drawAttitudeIndicator(painter);
    drawSpeedTape(painter);
    drawAltitudeTape(painter);
    drawHeadingIndicator(painter);
}

void PFDWidget::drawStatusBar(QPainter& painter)
{
    painter.save();
    
    painter.fillRect(m_statusRect, QColor(30, 30, 30));
    
    QFont font = painter.font();
    font.setPixelSize(12);
    font.setBold(true);
    painter.setFont(font);
    
    int x = 10;
    int y = m_statusRect.center().y() + 4;
    
    // GPS status
    painter.setPen(m_gpsOk ? OK_COLOR : DANGER_COLOR);
    painter.drawText(x, y, "GPS");
    x += 50;
    
    // Armed status
    painter.setPen(m_armed ? OK_COLOR : WARNING_COLOR);
    painter.drawText(x, y, m_armed ? "ARMED" : "DISARM");
    x += 70;
    
    // Mode
    painter.setPen(LINE_COLOR);
    painter.drawText(x, y, m_mode);
    x += 100;
    
    // Battery
    QColor batColor = m_batteryPercent > 50 ? OK_COLOR : 
                      (m_batteryPercent > 20 ? WARNING_COLOR : DANGER_COLOR);
    painter.setPen(batColor);
    painter.drawText(x, y, QString("BAT: %1%").arg(m_batteryPercent));
    
    painter.restore();
}

void PFDWidget::drawAttitudeIndicator(QPainter& painter)
{
    /**
     * TODO: Реализуйте отрисовку искусственного горизонта
     * 
     * Шаги:
     * 1. Сохранить состояние painter
     * 2. Установить clipping region на m_attitudeRect
     * 3. Переместить центр координат в центр rect
     * 4. Нарисовать небо/землю с учётом pitch и roll
     * 5. Нарисовать pitch ladder (шкала тангажа)
     * 6. Нарисовать roll indicator (треугольники вверху)
     * 7. Нарисовать aircraft symbol (статичный указатель)
     * 8. Восстановить состояние painter
     */
    
    painter.save();
    
    painter.setClipRect(m_attitudeRect);
    
    QPoint center = m_attitudeRect.center();
    int w = m_attitudeRect.width();
    int h = m_attitudeRect.height();
    
    // Перемещаем координаты в центр
    painter.translate(center);
    
    // Вращаем по крену
    painter.rotate(-m_roll);
    
    // Смещение по тангажу (пиксели на градус)
    qreal pitchPixels = h / 60.0;  // 60 градусов на весь экран
    qreal pitchOffset = m_pitch * pitchPixels;
    
    // Рисуем небо и землю
    QRect skyRect(-w, -h - pitchOffset, w * 2, h);
    QRect groundRect(-w, -pitchOffset, w * 2, h);
    
    QLinearGradient skyGradient(0, skyRect.top(), 0, skyRect.bottom());
    skyGradient.setColorAt(0, SKY_COLOR_TOP);
    skyGradient.setColorAt(1, SKY_COLOR_BOTTOM);
    painter.fillRect(skyRect, skyGradient);
    
    QLinearGradient groundGradient(0, groundRect.top(), 0, groundRect.bottom());
    groundGradient.setColorAt(0, GROUND_COLOR_TOP);
    groundGradient.setColorAt(1, GROUND_COLOR_BOTTOM);
    painter.fillRect(groundRect, groundGradient);
    
    // Линия горизонта
    painter.setPen(QPen(LINE_COLOR, 2));
    painter.drawLine(-w, -pitchOffset, w, -pitchOffset);
    
    // TODO: Нарисуйте pitch ladder
    // Линии каждые 10 градусов с подписями
    
    // TODO: Нарисуйте roll indicator
    
    // Сбрасываем вращение для статичных элементов
    painter.resetTransform();
    painter.translate(center);
    
    // Aircraft symbol (статичный)
    painter.setPen(QPen(INDICATOR_COLOR, 3));
    painter.drawLine(-40, 0, -15, 0);
    painter.drawLine(15, 0, 40, 0);
    painter.drawLine(-15, 0, -15, 8);
    painter.drawLine(15, 0, 15, 8);
    painter.drawLine(0, -5, 0, 5);
    
    painter.restore();
}

void PFDWidget::drawSpeedTape(QPainter& painter)
{
    /**
     * TODO: Реализуйте отрисовку ленты скорости
     * 
     * 1. Фон ленты
     * 2. Движущаяся шкала с делениями
     * 3. Текущее значение в рамке по центру
     */
    
    painter.save();
    painter.setClipRect(m_speedRect);
    
    // Фон
    painter.fillRect(m_speedRect, QColor(40, 40, 40, 200));
    
    QFont font = painter.font();
    font.setPixelSize(12);
    painter.setFont(font);
    
    int centerY = m_speedRect.center().y();
    qreal pixelsPerUnit = 5.0;  // пикселей на м/с
    
    // TODO: Нарисуйте шкалу
    // for (int spd = 0; spd <= 50; spd += 5) { ... }
    
    // Текущее значение
    painter.setPen(LINE_COLOR);
    painter.setBrush(QColor(0, 0, 0));
    QRect valueRect(m_speedRect.left() + 5, centerY - 12, m_speedRect.width() - 10, 24);
    painter.drawRect(valueRect);
    
    font.setPixelSize(16);
    font.setBold(true);
    painter.setFont(font);
    painter.drawText(valueRect, Qt::AlignCenter, QString::number(int(m_airspeed)));
    
    painter.restore();
}

void PFDWidget::drawAltitudeTape(QPainter& painter)
{
    // TODO: Аналогично drawSpeedTape, но справа
    
    painter.save();
    painter.setClipRect(m_altitudeRect);
    
    painter.fillRect(m_altitudeRect, QColor(40, 40, 40, 200));
    
    int centerY = m_altitudeRect.center().y();
    
    // Текущее значение
    QFont font = painter.font();
    font.setPixelSize(16);
    font.setBold(true);
    painter.setFont(font);
    painter.setPen(LINE_COLOR);
    painter.setBrush(QColor(0, 0, 0));
    
    QRect valueRect(m_altitudeRect.left() + 5, centerY - 12, m_altitudeRect.width() - 10, 24);
    painter.drawRect(valueRect);
    painter.drawText(valueRect, Qt::AlignCenter, QString::number(int(m_altitude)));
    
    painter.restore();
}

void PFDWidget::drawHeadingIndicator(QPainter& painter)
{
    /**
     * TODO: Реализуйте отрисовку компаса
     * 
     * 1. Фон
     * 2. Движущаяся шкала с делениями
     * 3. Кардинальные точки (N, E, S, W)
     * 4. Указатель текущего курса
     */
    
    painter.save();
    painter.setClipRect(m_headingRect);
    
    painter.fillRect(m_headingRect, QColor(40, 40, 40));
    
    int centerX = m_headingRect.center().x();
    int y = m_headingRect.top() + 25;
    
    QFont font = painter.font();
    font.setPixelSize(12);
    painter.setFont(font);
    painter.setPen(LINE_COLOR);
    
    // TODO: Нарисуйте шкалу компаса
    
    // Указатель курса (треугольник)
    QPainterPath triangle;
    triangle.moveTo(centerX, m_headingRect.top() + 5);
    triangle.lineTo(centerX - 8, m_headingRect.top() + 20);
    triangle.lineTo(centerX + 8, m_headingRect.top() + 20);
    triangle.closeSubpath();
    
    painter.setBrush(INDICATOR_COLOR);
    painter.drawPath(triangle);
    
    // Текущий курс
    font.setPixelSize(14);
    font.setBold(true);
    painter.setFont(font);
    painter.drawText(m_headingRect.right() - 80, y + 15, QString("HDG: %1°").arg(int(m_heading)));
    
    painter.restore();
}

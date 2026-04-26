# Задание 4: Primary Flight Display (PFD)

**Уровень:** Сложный  
**Технологии:** C++, Qt/QML  
**Время выполнения:** 10-14 часов

## Описание

Primary Flight Display (PFD) — основной инструмент пилота для отображения параметров полёта. Он показывает крен, тангаж, скорость, высоту и другие критические данные.

## Цель

Создать кастомный Qt виджет, который отображает:

1. Искусственный горизонт (крен, тангаж)
2. Индикатор скорости (лента слева)
3. Индикатор высоты (лента справа)
4. Компас (курс внизу)
5. Индикаторы режима и статуса

## Референс

```
┌─────────────────────────────────────────────────────────────┐
│  [GPS]    [ARM]    [AUTO]    [BAT: 85%]    [CONN]         │
├───────┬─────────────────────────────────────────┬──────────┤
│       │              ╱╲                          │          │
│  45 ──│            ╱    ╲                        │── 180    │
│       │          ╱   ◇    ╲                      │          │
│  40 ──│═════════╱══════════╲═════════════════════│── 170    │
│       │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│          │
│  35 ──│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│── 160    │
│   ▲   │▓▓▓▓▓▓▓▓▓▓▓▓ ЗЕМЛЯ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│   ▼      │
│  SPD  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  ALT     │
├───────┴─────────────────────────────────────────┴──────────┤
│              270    ▼    090                               │
│         W  ─────────┼─────────  E          HDG: 315°       │
└─────────────────────────────────────────────────────────────┘
```

## Компоненты

### 1. Искусственный горизонт (Attitude Indicator)

- Вращается по крену (roll)
- Смещается по тангажу (pitch)
- Небо (голубое) вверху, земля (коричневая) внизу
- Шкала тангажа -90° до +90°
- Индикатор нулевого крена (треугольник вверху)
- Указатель самолёта (статичный центр)

### 2. Индикатор скорости (Speed Tape)

- Вертикальная лента слева
- Движется вверх/вниз
- Текущая скорость в центре с рамкой
- Цветные зоны (зелёная - норма, жёлтая - предупреждение)
- Тренд скорости (стрелка)

### 3. Индикатор высоты (Altitude Tape)

- Вертикальная лента справа
- Аналогично speed tape
- Относительная высота

### 4. Компас (Heading Indicator)

- Горизонтальная лента внизу
- Текущий курс с указателем
- Кардинальные точки (N, E, S, W)

## Что нужно реализовать

### QML компонент

```qml
// PFD.qml
Item {
    id: pfd
    
    // Входные данные
    property real roll: 0       // -180..180
    property real pitch: 0      // -90..90
    property real heading: 0    // 0..360
    property real airspeed: 0   // м/с
    property real altitude: 0   // м
    property real verticalSpeed: 0
    property bool armed: false
    property string mode: "STABILIZE"
    property int batteryPercent: 100
    property bool gpsOk: true
    property bool connected: true
    
    // Компоненты
    AttitudeIndicator { ... }
    SpeedTape { ... }
    AltitudeTape { ... }
    HeadingIndicator { ... }
    StatusBar { ... }
}
```

### Или Qt Widgets + QPainter

```cpp
class PFDWidget : public QWidget {
    Q_OBJECT
    Q_PROPERTY(qreal roll READ roll WRITE setRoll)
    Q_PROPERTY(qreal pitch READ pitch WRITE setPitch)
    // ...
    
protected:
    void paintEvent(QPaintEvent* event) override;
    
private:
    void drawAttitudeIndicator(QPainter& painter, const QRect& rect);
    void drawSpeedTape(QPainter& painter, const QRect& rect);
    void drawAltitudeTape(QPainter& painter, const QRect& rect);
    void drawHeadingIndicator(QPainter& painter, const QRect& rect);
    void drawStatusBar(QPainter& painter, const QRect& rect);
};
```

## Структура проекта

```
src/
├── main.cpp
├── pfd_widget.h/cpp       # Qt Widgets версия
├── qml/
│   ├── main.qml
│   ├── PFD.qml
│   ├── AttitudeIndicator.qml
│   ├── SpeedTape.qml
│   ├── AltitudeTape.qml
│   └── HeadingIndicator.qml
└── resources/
    ├── images/
    └── fonts/
tests/
└── test_pfd.cpp
```

## Запуск

```bash
cd hard/04-cpp-custom-widget

# Qt Widgets
qmake
make
./pfd_demo

# QML
qmlscene src/qml/main.qml
```

## Демо приложение

Демо должно:
1. Показывать PFD
2. Иметь слайдеры для изменения параметров
3. Имитировать реальные данные (кнопка "Simulate")

## Критерии оценки

- [ ] Искусственный горизонт работает корректно
- [ ] Speed tape показывает скорость
- [ ] Altitude tape показывает высоту
- [ ] Компас показывает курс
- [ ] Статус бар с индикаторами
- [ ] Плавная анимация (60 FPS)
- [ ] Корректное масштабирование
- [ ] Визуальное соответствие референсу

## Подсказки

1. Используйте `QTransform` для вращения
2. Градиенты для неба/земли: `QLinearGradient`
3. Clipping для масок: `QPainterPath`
4. Антиалиасинг: `QPainter::Antialiasing`
5. Для QML: `Canvas` или `ShaderEffect`

## Цветовая схема

```
Небо:       #87CEEB -> #4682B4 (градиент)
Земля:      #8B4513 -> #D2691E (градиент)
Линия:      #FFFFFF
Указатели:  #FFFF00 (жёлтый)
Опасность:  #FF0000
Предупреждение: #FFA500
Норма:      #00FF00
```

## Дополнительно (необязательно)

- Flight Director (FD) bars
- Flight Path Vector (FPV)
- Synthetic vision (3D terrain)
- Night mode

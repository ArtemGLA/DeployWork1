# Задание 4: Parameter Editor

**Уровень:** Средний  
**Технологии:** C++, Qt Widgets  
**Время выполнения:** 5-7 часов

## Описание

Дроны имеют сотни настраиваемых параметров: PID коэффициенты, лимиты скорости, failsafe настройки и т.д. Parameter Editor — это GUI инструмент для их просмотра и редактирования.

## Цель

Создать Qt приложение, которое:

1. Загружает схему параметров из JSON
2. Отображает параметры в таблице с группировкой
3. Позволяет редактировать значения с валидацией
4. Поддерживает сохранение/загрузку профилей
5. Показывает описания параметров

## Макет

```
┌─────────────────────────────────────────────────────────────┐
│  File  Edit  View  Help                                     │
├─────────────────────────────────────────────────────────────┤
│  [🔍 Search...]          [Load Profile ▼] [Save] [Reset All]│
├──────────────┬──────────────────────────────────────────────┤
│  Categories  │  Parameter Table                             │
│  ┌─────────┐ │  ┌──────────────┬──────────┬────────────────┐│
│  │ ▼ PID   │ │  │ Name         │ Value    │ Default        ││
│  │   Roll  │ │  ├──────────────┼──────────┼────────────────┤│
│  │   Pitch │ │  │ ATC_RAT_RLL_P│ 0.135    │ 0.135          ││
│  │   Yaw   │ │  │ ATC_RAT_RLL_I│ 0.135    │ 0.135          ││
│  │ ▼ Limits│ │  │ ATC_RAT_RLL_D│ 0.0036   │ 0.0036         ││
│  │   Speed │ │  │ ...          │          │                ││
│  │   Angle │ │  └──────────────┴──────────┴────────────────┘│
│  │ ▶ Failsafe│                                              │
│  │ ▶ Battery│ ┌──────────────────────────────────────────────┤
│  │ ...     │ │ Description:                                 │
│  └─────────┘ │ ATC_RAT_RLL_P - Roll axis rate controller    │
│              │ P gain. Converts roll rate error to motor    │
│              │ output. Range: 0.01-0.5, Increment: 0.005    │
└──────────────┴──────────────────────────────────────────────┘
```

## Формат схемы параметров

```json
{
  "version": "1.0",
  "vehicle": "ArduCopter",
  "groups": [
    {
      "name": "PID",
      "description": "PID Controller Settings",
      "subgroups": [
        {
          "name": "Roll",
          "parameters": [
            {
              "name": "ATC_RAT_RLL_P",
              "displayName": "Roll Rate P",
              "description": "Roll axis rate controller P gain",
              "type": "float",
              "default": 0.135,
              "min": 0.01,
              "max": 0.5,
              "increment": 0.005,
              "units": ""
            }
          ]
        }
      ]
    }
  ]
}
```

## Что нужно реализовать

### 1. Главное окно `MainWindow`

```cpp
class MainWindow : public QMainWindow {
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = nullptr);
    
private slots:
    void loadSchema();
    void saveProfile();
    void loadProfile();
    void resetAllToDefault();
    void onParameterChanged(const QString& name, const QVariant& value);
    void onCategorySelected(const QModelIndex& index);
    void onSearchTextChanged(const QString& text);
    
private:
    void setupUI();
    void setupMenuBar();
    void populateCategories();
    void showParametersForCategory(const QString& category);
    
    ParameterSchema m_schema;
    QMap<QString, QVariant> m_values;
    QMap<QString, QVariant> m_modifiedValues;
    
    // UI elements
    QTreeView* m_categoryTree;
    QTableView* m_parameterTable;
    QTextEdit* m_descriptionView;
    QLineEdit* m_searchBox;
};
```

### 2. Модель параметров `ParameterModel`

```cpp
class ParameterModel : public QAbstractTableModel {
    Q_OBJECT
    
public:
    enum Column { Name, Value, Default, Units, ColumnCount };
    
    void setParameters(const QList<Parameter>& params);
    void setValues(const QMap<QString, QVariant>& values);
    
    // QAbstractTableModel interface
    int rowCount(const QModelIndex& parent) const override;
    int columnCount(const QModelIndex& parent) const override;
    QVariant data(const QModelIndex& index, int role) const override;
    bool setData(const QModelIndex& index, const QVariant& value, int role) override;
    Qt::ItemFlags flags(const QModelIndex& index) const override;
    QVariant headerData(int section, Qt::Orientation, int role) const override;
    
signals:
    void parameterChanged(const QString& name, const QVariant& value);
    
private:
    QList<Parameter> m_parameters;
    QMap<QString, QVariant> m_values;
};
```

### 3. Делегат редактирования `ParameterDelegate`

```cpp
class ParameterDelegate : public QStyledItemDelegate {
    Q_OBJECT
    
public:
    QWidget* createEditor(QWidget* parent, const QStyleOptionViewItem& option,
                         const QModelIndex& index) const override;
    void setEditorData(QWidget* editor, const QModelIndex& index) const override;
    void setModelData(QWidget* editor, QAbstractItemModel* model,
                     const QModelIndex& index) const override;
                     
private:
    // Создаёт правильный виджет в зависимости от типа параметра
    QWidget* createEditorForType(QWidget* parent, const Parameter& param) const;
};
```

### 4. Валидация

- Числа: проверка min/max диапазона
- Enum: выпадающий список с допустимыми значениями
- Bool: чекбокс
- Подсветка изменённых значений (отличаются от default)

## Структура проекта

```
src/
├── main.cpp
├── mainwindow.h/cpp       # Главное окно (реализовать)
├── parametermodel.h/cpp   # Модель данных (реализовать)
├── parameterdelegate.h/cpp # Делегат (реализовать)
├── parameterschema.h/cpp  # Загрузка схемы (частично готово)
└── parameter.h            # Структуры данных (готово)
data/
├── schema.json            # Схема параметров
└── default_profile.json   # Профиль по умолчанию
```

## Сборка и запуск

```bash
cd medium/04-cpp-parameter-editor

# Qmake
qmake
make

# Или CMake
mkdir build && cd build
cmake ..
make

# Запуск
./parameter-editor
```

## Критерии оценки

- [ ] Загрузка и парсинг JSON схемы
- [ ] Отображение параметров с группировкой
- [ ] Редактирование с правильными виджетами
- [ ] Валидация значений
- [ ] Сохранение/загрузка профилей
- [ ] Поиск по параметрам
- [ ] Подсветка изменённых значений

## Подсказки

1. Используйте `QJsonDocument` для парсинга JSON
2. `QSortFilterProxyModel` для поиска
3. Разные виджеты в делегате: `QDoubleSpinBox`, `QComboBox`, `QCheckBox`
4. `QSettings` для запоминания последнего профиля
5. `QStandardItemModel` для дерева категорий

## Дополнительно (необязательно)

- Импорт/экспорт в формате ArduPilot
- Сравнение двух профилей
- Undo/Redo для изменений
- Графики зависимостей параметров

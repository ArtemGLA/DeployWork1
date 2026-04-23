#pragma once

#include <QString>
#include <QVariant>
#include <QList>
#include <QJsonObject>

/// Тип параметра.
enum class ParameterType {
    Float,
    Int,
    Bool,
    Enum,
    String
};

/// Значение enum параметра.
struct EnumValue {
    int value;
    QString name;
    QString description;
};

/// Параметр дрона.
struct Parameter {
    QString name;           // Имя параметра (ATC_RAT_RLL_P)
    QString displayName;    // Отображаемое имя
    QString description;    // Описание
    QString group;          // Группа
    QString subgroup;       // Подгруппа
    
    ParameterType type = ParameterType::Float;
    QVariant defaultValue;
    QVariant minValue;
    QVariant maxValue;
    double increment = 0.0;
    QString units;
    
    QList<EnumValue> enumValues;  // Для Enum типа
    
    /// Парсинг из JSON.
    static Parameter fromJson(const QJsonObject& obj, const QString& group, const QString& subgroup);
    
    /// Валидация значения.
    bool validate(const QVariant& value) const;
    
    /// Форматирование значения для отображения.
    QString formatValue(const QVariant& value) const;
};

/// Группа подпараметров.
struct ParameterSubgroup {
    QString name;
    QList<Parameter> parameters;
};

/// Группа параметров.
struct ParameterGroup {
    QString name;
    QString description;
    QList<ParameterSubgroup> subgroups;
};

/// Схема параметров.
struct ParameterSchema {
    QString version;
    QString vehicle;
    QList<ParameterGroup> groups;
    
    /// Загрузить из JSON файла.
    static ParameterSchema load(const QString& filepath);
    
    /// Получить все параметры плоским списком.
    QList<Parameter> allParameters() const;
    
    /// Найти параметр по имени.
    Parameter* findParameter(const QString& name);
};

#include "parametermodel.h"
#include <QList>
#include <QVariant>
#include <QDebug>

ParameterModel::ParameterModel(QObject *parent) : QAbstractTableModel(parent) {
    // Заполнение данных

    m_values = {
        {"Tom", 10},
        {"Bob", 20},
        {"Sam", 30}
    };
}

int ParameterModel::rowCount(const QModelIndex &parent) const {
    return parent.isValid() ? 0 : m_values.size();
}

int ParameterModel::columnCount(const QModelIndex &parent) const {
    return 3;
}

QVariant ParameterModel::data(const QModelIndex &index, int role) const {

        if (!index.isValid())
        return QVariant();
    
    // Для кастомных ролей
    if (role == ParamMinRole || role == ParamMaxRole) {
        if (index.column() == 1) {  // Только для колонки Value
            QString paramName = m_values.keys()[index.row()];
            // Ищем параметр в m_subgroupCurrent
            for (const auto& param : m_subgroupCurrent.parameters) {
                if (param.displayName == paramName) {
                    if (role == ParamMinRole) return param.minValue;
                    else return param.maxValue;
                }
            }
        }
        return QVariant();
    }

    if (!index.isValid() || (role != Qt::DisplayRole && role != Qt::EditRole))
        return QVariant();

    
    if (index.column() == 0 && role != Qt::EditRole)
        return m_values.keys()[index.row()];

    else if (index.column() == 1) {

        return m_values.values()[index.row()];
    }

    else if (index.column() == 2 && role != Qt::EditRole)
        return m_values.values()[index.row()];
}

QVariant ParameterModel::headerData(int section, Qt::Orientation orientation, int role) const {
    if (role != Qt::DisplayRole || orientation != Qt::Horizontal)
        return QVariant();
    
    if (section == 0) return "Name";
    if (section == 1) return "Value";
    if (section == 2) return "Default";
}

void ParameterModel::addValue(const QString& key, const QVariant& value)
{
    int newRow = m_values.size(); // Индекс новой строки
    
    beginInsertRows(QModelIndex(), newRow, newRow);
    m_values.insert(key, value);
    endInsertRows();
}

Qt::ItemFlags ParameterModel::flags(const QModelIndex &index) const
{
    if (!index.isValid())
        return Qt::NoItemFlags;
    
    Qt::ItemFlags flags = QAbstractTableModel::flags(index);
    
    // Разрешаем редактирование для колонки возраста (индекс 1)
    if (index.column() == 1) {
        flags |= Qt::ItemIsEditable;  // Вот этот флаг критически важен!
    }
    
    return flags;
}

void ParameterModel::clear()
{
    
    beginResetModel();
    m_values.clear();
    endResetModel();
}

bool ParameterModel::setData(const QModelIndex &index, const QVariant &value, int role)
{
    if (!index.isValid() || role != Qt::EditRole)
        return false;
    
    if (index.column() == 1) {
        bool ok;
        double newAge = value.toDouble(&ok);
        
        if (ok && newAge >= 0 && newAge <= 150) {
            int row = index.row();
            
            // Получаем ключ по индексу строки
            QString key = m_values.keys()[row];
            
            // Обновляем значение в map по ключу
            m_values[key] = newAge;  // ✅ ПРАВИЛЬНО
            
            // Уведомляем об изменении
            emit dataChanged(index, index, {Qt::DisplayRole, Qt::EditRole});
            return true;
        }
    }
    
    return false;
}

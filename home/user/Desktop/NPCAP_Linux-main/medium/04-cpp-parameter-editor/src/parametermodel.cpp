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

    if (!index.isValid() || role != Qt::DisplayRole)
        return QVariant();

    
    if (index.column() == 0)
        return m_values.keys()[index.row()];

    else if (index.column() == 1) {

        return m_values.values()[index.row()];
    }

    else if (index.column() == 2)
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

void ParameterModel::clear()
{
    
    beginResetModel();
    m_values.clear();
    endResetModel();
}

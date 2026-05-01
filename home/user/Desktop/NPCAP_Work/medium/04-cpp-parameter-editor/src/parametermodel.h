#ifndef PARAMETERMODEL_H
#define PARAMETERMODEL_H
#include "parameter.h"

#include <QAbstractTableModel>

enum ParameterRoles {
    ParamIncrement = Qt::UserRole + 3,
    ParamMinRole = Qt::UserRole + 2,
    ParamMaxRole = Qt::UserRole + 1
};

class ParameterModel : public QAbstractTableModel {
    Q_OBJECT

public:
    explicit ParameterModel(QObject *parent = nullptr);
    
    // Переопределенные функции
    int rowCount(const QModelIndex &parent = QModelIndex()) const override;
    int columnCount(const QModelIndex &parent = QModelIndex()) const override;
    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const override;
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
    Qt::ItemFlags flags(const QModelIndex &index) const;
    void addValue(const QString& key, const QVariant& value, const QVariant& defaultValue);
    bool setData(const QModelIndex &index, const QVariant &value, int role);
    void clear();

    QList<Parameter> m_parameters;
    ParameterSubgroup m_subgroupCurrent;    //Для Description
    Parameter m_parameterCurent;    //Для Description
    QMap<QString, QList<QVariant>> m_values;
};

#endif // PARAMETERMODEL_H

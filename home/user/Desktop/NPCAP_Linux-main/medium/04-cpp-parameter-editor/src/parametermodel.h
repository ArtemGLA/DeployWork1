#ifndef PARAMETERMODEL_H
#define PARAMETERMODEL_H
#include "parameter.h"

#include <QAbstractTableModel>

class ParameterModel : public QAbstractTableModel {
    Q_OBJECT

public:
    explicit ParameterModel(QObject *parent = nullptr);
    
    // Переопределенные функции
    int rowCount(const QModelIndex &parent = QModelIndex()) const override;
    int columnCount(const QModelIndex &parent = QModelIndex()) const override;
    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const override;
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
    void addValue(const QString& key, const QVariant& value);
    void clear();

    QList<Parameter> m_parameters;
    Parameter m_parameterCureent;    //Для Description
    QMap<QString, QVariant> m_values;
};

#endif // PARAMETERMODEL_H

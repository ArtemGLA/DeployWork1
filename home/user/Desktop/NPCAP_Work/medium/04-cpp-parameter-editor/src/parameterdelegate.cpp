#include "parameterdelegate.h"
#include "parametermodel.h"
#include <QDoubleSpinBox>
#include <QApplication>

ParameterDelegate::ParameterDelegate(QObject *parent)
    : QStyledItemDelegate(parent)
{
}

QWidget* ParameterDelegate::createEditor(QWidget *parent, const QStyleOptionViewItem &option,
                                   const QModelIndex &index) const
{
    Q_UNUSED(option);

    int typeInt = index.data(ParamType).toInt();
    ParameterType type = static_cast<ParameterType>(typeInt);

    if (type == ParameterType::Float)
    {
        // Получаем мин/макс из модели
        double minVal = index.data(ParamMinRole).toDouble();
        double maxVal = index.data(ParamMaxRole).toDouble();
        double increment = index.data(ParamIncrement).toDouble();
        double defaultValue = index.data(ParamDefault).toDouble();

        
        QDoubleSpinBox *spinBox = new QDoubleSpinBox(parent);
        if (minVal != 0 || maxVal != 0) {  // Если есть ограничения
            spinBox->setRange(minVal, maxVal);
        } else {
            spinBox->setRange(-999999, 999999);  // Дефолтный диапазон
        }

        spinBox->setSingleStep(increment);

        spinBox->setDecimals(calculateDecimals(defaultValue)); 
        
        return spinBox;
    }
}

void ParameterDelegate::setEditorData(QWidget *editor, const QModelIndex &index) const
{
    QDoubleSpinBox *spinBox = qobject_cast<QDoubleSpinBox*>(editor);
    if (spinBox) {
        // Берем текущее значение из модели и устанавливаем в spinbox
        double value = index.data(Qt::EditRole).toDouble();
        spinBox->setValue(value);
    }
}

void ParameterDelegate::setModelData(QWidget *editor, QAbstractItemModel *model,
                               const QModelIndex &index) const
{
    QDoubleSpinBox *spinBox = qobject_cast<QDoubleSpinBox*>(editor);
    if (spinBox) {
        // Получаем новое значение из spinbox и сохраняем в модель
        double newValue = spinBox->value();
        model->setData(index, newValue, Qt::EditRole);
    }
}

void ParameterDelegate::updateEditorGeometry(QWidget *editor, const QStyleOptionViewItem &option,
                                       const QModelIndex &index) const
{
    Q_UNUSED(index);
    // Просто подставляем редактор под размер ячейки
    editor->setGeometry(option.rect);
}

int ParameterDelegate::calculateDecimals(double value) const
{
    // Преобразуем в строку и считаем знаки после точки
    QString str = QString::number(value, 'f', 15); // Используем 15 знаков для точности
    str.remove(QRegularExpression("0+$")); // Удаляем trailing zeros
    int dotPos = str.indexOf('.');
    if (dotPos == -1) return 0;
    return str.length() - dotPos - 1;
}

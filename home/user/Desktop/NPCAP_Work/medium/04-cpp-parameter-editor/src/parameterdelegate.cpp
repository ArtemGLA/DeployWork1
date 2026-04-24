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
    
    // Получаем мин/макс из модели
    double minVal = index.data(ParamMinRole).toDouble();
    double maxVal = index.data(ParamMaxRole).toDouble();
    
    QDoubleSpinBox *spinBox = new QDoubleSpinBox(parent);
    if (minVal != 0 || maxVal != 0) {  // Если есть ограничения
        spinBox->setRange(minVal, maxVal);
    } else {
        spinBox->setRange(-999999, 999999);  // Дефолтный диапазон
    }
    
    return spinBox;
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

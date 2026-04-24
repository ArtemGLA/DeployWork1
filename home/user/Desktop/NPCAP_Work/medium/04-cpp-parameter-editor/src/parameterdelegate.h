#ifndef DELEGATE_H
#define DELEGATE_H

#include <QStyledItemDelegate>

class ParameterDelegate : public QStyledItemDelegate
{
    Q_OBJECT

public:
    explicit ParameterDelegate(QObject *parent = nullptr);
    
    // Создание редактора (QDoubleSpinBox)
    QWidget* createEditor(QWidget *parent, const QStyleOptionViewItem &option,
                         const QModelIndex &index) const override;
    
    // Установка данных в редактор
    void setEditorData(QWidget *editor, const QModelIndex &index) const override;
    
    // Сохранение данных из редактора в модель
    void setModelData(QWidget *editor, QAbstractItemModel *model,
                     const QModelIndex &index) const override;
    
    // Обновление размеров редактора под размер ячейки
    void updateEditorGeometry(QWidget *editor, const QStyleOptionViewItem &option,
                             const QModelIndex &index) const override;
};

#endif // DELEGATE_H

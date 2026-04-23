#pragma once

#include <QMainWindow>
#include <QTreeView>
#include <QTableView>
#include <QTextEdit>
#include <QLineEdit>
#include <QStandardItemModel>
#include <QSortFilterProxyModel>
#include "parameter.h"

class ParameterModel;
class ParameterDelegate;

/**
 * Главное окно редактора параметров.
 * 
 * TODO: Реализуйте методы в mainwindow.cpp
 */
class MainWindow : public QMainWindow {
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
    
private slots:
    /// Загрузить схему параметров.
    void loadSchema();
    
    /// Сохранить текущий профиль.
    void saveProfile();
    
    /// Загрузить профиль из файла.
    void loadProfile();
    
    /// Сбросить все параметры к значениям по умолчанию.
    void resetAllToDefault();
    
    /// Обработчик изменения параметра.
    void onParameterChanged(const QString& name, const QVariant& value);
    
    /// Обработчик выбора категории.
    void onCategorySelected(const QModelIndex& index);
    
    /// Обработчик изменения текста поиска.
    void onSearchTextChanged(const QString& text);
    
    /// Показать описание выбранного параметра.
    void onParameterSelected(const QModelIndex& index);
    
private:
    /// Настройка UI элементов.
    void setupUI();
    
    /// Создание меню.
    void setupMenuBar();
    
    /// Создание тулбара.
    void setupToolBar();
    
    /// Заполнение дерева категорий.
    void populateCategories();
    
    /// Показать параметры выбранной категории.
    void showParametersForCategory(const QString& group, const QString& subgroup);
    
    /// Обновить описание параметра.
    void updateDescription(const Parameter& param);
    
    // Data
    ParameterSchema m_schema;
    QMap<QString, QVariant> m_currentValues;
    QMap<QString, QVariant> m_modifiedValues;
    QString m_currentProfilePath;
    
    // UI elements
    QTreeView* m_categoryTree;
    QStandardItemModel* m_categoryModel;
    
    QTableView* m_parameterTable;
    ParameterModel* m_parameterModel;
    QSortFilterProxyModel* m_filterModel;
    ParameterDelegate* m_delegate;
    
    QTextEdit* m_descriptionView;
    QLineEdit* m_searchBox;
};

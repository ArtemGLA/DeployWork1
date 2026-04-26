#include "mainwindow.h"
#include "parametermodel.h"
#include "parameterdelegate.h"

#include <QMenuBar>
#include <QToolBar>
#include <QStatusBar>
#include <QSplitter>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QPushButton>
#include <QFileDialog>
#include <QMessageBox>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent)
{
    setWindowTitle("Parametter Editor");
    resize(1000, 700);

    setupUI();
    setupMenuBar();
    setupToolBar();
}

void MainWindow::setupUI()
{
    auto* centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);
    
    auto* mainLayout = new QVBoxLayout(centralWidget);
    
    // Поисковая строка
    auto* searchLayout = new QHBoxLayout();
    m_searchBox = new QLineEdit();
    m_searchBox->setPlaceholderText("Search parameters...");
    searchLayout->addWidget(m_searchBox);
    
    auto* resetBtn = new QPushButton("Reset All");
    searchLayout->addWidget(resetBtn);
    
    mainLayout->addLayout(searchLayout);
    
    // Основной сплиттер
    auto* splitter = new QSplitter(Qt::Horizontal);
    
    // Дерево категорий
    m_categoryTree = new QTreeView();
    m_categoryModel = new QStandardItemModel(this);
    m_categoryTree->setModel(m_categoryModel);
    m_categoryTree->setHeaderHidden(true);
    m_categoryTree->setMinimumWidth(200);
    splitter->addWidget(m_categoryTree);
    
    // Правая панель
    auto* rightWidget = new QWidget();
    auto* rightLayout = new QVBoxLayout(rightWidget);
    
    // Таблица параметров
    m_parameterTable = new QTableView();
    // TODO: Создайте ParameterModel и установите его
    m_parameterModel = new ParameterModel(this);
    m_filterModel = new QSortFilterProxyModel(this);
    m_filterModel->setSourceModel(m_parameterModel);
    m_parameterTable->setModel(m_filterModel);
    
    // TODO: Создайте ParameterDelegate
    m_delegate = new ParameterDelegate(this);
    m_parameterTable->setItemDelegate(m_delegate);
    
    rightLayout->addWidget(m_parameterTable, 3);
    
    // Описание параметра
    auto* descGroup = new QGroupBox("Description");
    auto* descLayout = new QVBoxLayout(descGroup);
    m_descriptionView = new QTextEdit();
    m_descriptionView->setReadOnly(true);
    m_descriptionView->setMaximumHeight(100);
    descLayout->addWidget(m_descriptionView);
    rightLayout->addWidget(descGroup);
    
    splitter->addWidget(rightWidget);
    splitter->setStretchFactor(0, 1);
    splitter->setStretchFactor(1, 3);
    
    mainLayout->addWidget(splitter);

    connect(m_searchBox, &QLineEdit::textChanged, 
            this, &MainWindow::onSearchTextChanged);
    connect(m_categoryTree->selectionModel(), &QItemSelectionModel::currentChanged,
        this, &MainWindow::onCategorySelected);

    connect(m_parameterTable->selectionModel(), &QItemSelectionModel::currentChanged,
        this, &MainWindow::onParameterSelected);
}

    /// Создание меню.
void MainWindow::setupMenuBar()
{
    auto* fileMenu = menuBar()->addMenu("&File");

    auto* loadSchemaAction = fileMenu->addAction("Load Schema...");
    connect(loadSchemaAction, &QAction::triggered, this, &MainWindow::loadSchema);

    auto* loadProfileAction = fileMenu->addAction("Load Profile...");

    auto* saveProfileAction = fileMenu->addAction("Save Profile");

    fileMenu->addSeparator();

    auto* exitAction = fileMenu->addAction("Exit");

    auto* editMenu = menuBar()->addMenu("&Edit");

    auto* resetAllToDefaultAction = editMenu->addAction("Reset All to Default");
    auto* resetSelectedToDefaultAction = editMenu->addAction("Reset Selected to Default");
    
    auto* helpMenu = menuBar()->addMenu("&Help");

    auto* aboutAction = helpMenu->addAction("About");
}

void MainWindow::setupToolBar()
{
    // TODO: Создайте тулбар с основными действиями
    
    auto* toolbar = addToolBar("Main");
    toolbar->addAction("Load");
    toolbar->addAction("Save");
    toolbar->addSeparator();
    toolbar->addAction("Reset");
}

void MainWindow::loadSchema()
{    
    QString filepath = QFileDialog::getOpenFileName(
        this, "Open Schema", "", "JSON Files (*.json)"
    );
    
    if (filepath.isEmpty()) return;
    
    m_schema = ParameterSchema::load(filepath);
    populateCategories();
    populateModelParameters();
    
    statusBar()->showMessage("Schema loaded: " + filepath);
}

void MainWindow::populateCategories()
{    
    m_categoryModel->clear();
    
    for (const auto& group : m_schema.groups) {
        auto* groupItem = new QStandardItem(group.name);
        for (const auto& subgroup : group.subgroups) {
            auto* subItem = new QStandardItem(subgroup.name);
            groupItem->appendRow(subItem);
        }
        m_categoryModel->appendRow(groupItem);
    }
}

// Заполнение списка параметров модели
void MainWindow::populateModelParameters()
{     
    for (const auto& group : m_schema.groups) {
        auto* groupItem = new QStandardItem(group.name);
        for (const auto& subgroup : group.subgroups) {
            auto* subItem = new QStandardItem(subgroup.name);
            for (auto& param : subgroup.parameters) {
                m_parameterModel->m_parameters.append(param);
            }
        }
    }
}

void MainWindow::onCategorySelected(const QModelIndex &index) {
    if (!index.isValid()) return;
    
    // Получаем имена группы и подгруппы
    QString subItemName = index.data().toString();  // "PID controller"
    QString groupItemName = index.parent().data().toString();  // "PID"
    
    
    // Ищем subgroup для отображения description
    for (auto& group : m_schema.groups) {
        if (group.name == groupItemName) {
            for (auto& subgroup : group.subgroups) {
                if (subgroup.name == subItemName) {
                    m_parameterModel->m_subgroupCurrent = subgroup;
                }
            }
        }
    }

    // Заполняем Model из списка 
    m_parameterModel->clear();
    for (auto& param : m_parameterModel->m_parameters) {
    if ((param.group == groupItemName) && (param.subgroup == subItemName)) {
            m_parameterModel->addValue(param.displayName, param.value, param.defaultValue);
        }
    }
    return;
}

void MainWindow::onParameterSelected(const QModelIndex &index) {
    // Проверяем, что индекс валидный
    if (!index.isValid()) return;
    
    // Получаем значение из первого столбца (column = 0) для текущей строки
    QModelIndex firstColumnIndex = index.sibling(index.row(), 0);
    QString value = index.model()->data(firstColumnIndex).toString();

    for (auto& param : m_parameterModel->m_subgroupCurrent.parameters)
    {
        if(param.displayName == value)
        {
            m_parameterModel->m_parameterCurent = param;
            updateDescription(param);
        }
    }
}

void MainWindow::onSearchTextChanged(const QString& text)
{    
    // Создаем регулярное выражение для поиска (регистронезависимо)
    QRegularExpression regex(text, QRegularExpression::CaseInsensitiveOption);
    
    // Применяем фильтр
    m_filterModel->setFilterRegularExpression(regex);
}

void MainWindow::updateDescription(const Parameter& param)
{
    // TODO: Обновить текст описания
    
    QString html = QString("<b>%1</b> (%2)<br><br>%3<br><br>"
                          "Range: %4 - %5<br>"
                          "Default: %6<br>"
                          "Units: %7")
        .arg(param.displayName)
        .arg(param.name)
        .arg(param.description)
        .arg(param.minValue.toString())
        .arg(param.maxValue.toString())
        .arg(param.defaultValue.toString())
        .arg(param.units.isEmpty() ? "-" : param.units);
    
    m_descriptionView->setHtml(html);
}
/**
 * MainWindow - реализация главного окна редактора параметров.
 * 
 * TODO: Реализуйте все методы.
 */

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

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , m_categoryTree(nullptr)
    , m_categoryModel(nullptr)
    , m_parameterTable(nullptr)
    , m_parameterModel(nullptr)
    , m_filterModel(nullptr)
    , m_delegate(nullptr)
    , m_descriptionView(nullptr)
    , m_searchBox(nullptr)
{
    setWindowTitle("Parameter Editor");
    resize(1000, 700);
    
    setupUI();
    setupMenuBar();
    setupToolBar();
    
    statusBar()->showMessage("Ready");
}

MainWindow::~MainWindow() = default;

void MainWindow::setupUI()
{
    // TODO: Создайте UI
    //
    // Структура:
    // - Центральный виджет с QSplitter
    // - Левая панель: QTreeView для категорий
    // - Правая панель: QTableView для параметров + QTextEdit для описания
    // - Сверху: поле поиска + кнопки
    
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
    // m_parameterModel = new ParameterModel(this);
    // m_filterModel = new QSortFilterProxyModel(this);
    // m_filterModel->setSourceModel(m_parameterModel);
    // m_parameterTable->setModel(m_filterModel);
    
    // TODO: Создайте ParameterDelegate
    // m_delegate = new ParameterDelegate(this);
    // m_parameterTable->setItemDelegate(m_delegate);
    
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
    
    // Подключение сигналов
    connect(m_searchBox, &QLineEdit::textChanged, 
            this, &MainWindow::onSearchTextChanged);
    connect(m_categoryTree->selectionModel(), &QItemSelectionModel::currentChanged,
            this, &MainWindow::onCategorySelected);
    connect(resetBtn, &QPushButton::clicked,
            this, &MainWindow::resetAllToDefault);
}

void MainWindow::setupMenuBar()
{
    // TODO: Создайте меню
    //
    // File:
    //   - Load Schema...
    //   - Load Profile...
    //   - Save Profile
    //   - Save Profile As...
    //   - Exit
    //
    // Edit:
    //   - Reset All to Default
    //   - Reset Selected to Default
    //
    // Help:
    //   - About
    
    auto* fileMenu = menuBar()->addMenu("&File");
    
    auto* loadSchemaAction = fileMenu->addAction("Load Schema...");
    connect(loadSchemaAction, &QAction::triggered, this, &MainWindow::loadSchema);
    
    auto* loadProfileAction = fileMenu->addAction("Load Profile...");
    connect(loadProfileAction, &QAction::triggered, this, &MainWindow::loadProfile);
    
    auto* saveProfileAction = fileMenu->addAction("Save Profile");
    connect(saveProfileAction, &QAction::triggered, this, &MainWindow::saveProfile);
    
    fileMenu->addSeparator();
    
    auto* exitAction = fileMenu->addAction("Exit");
    connect(exitAction, &QAction::triggered, this, &QMainWindow::close);
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
    // TODO: Реализуйте загрузку схемы
    //
    // 1. Открыть диалог выбора файла
    // 2. Загрузить JSON схему
    // 3. Заполнить дерево категорий
    // 4. Инициализировать значения по умолчанию
    
    QString filepath = QFileDialog::getOpenFileName(
        this, "Open Schema", "", "JSON Files (*.json)"
    );
    
    if (filepath.isEmpty()) return;
    
    // m_schema = ParameterSchema::load(filepath);
    // populateCategories();
    
    statusBar()->showMessage("Schema loaded: " + filepath);
}

void MainWindow::saveProfile()
{
    // TODO: Сохранить текущие значения в профиль
    
    if (m_currentProfilePath.isEmpty()) {
        QString filepath = QFileDialog::getSaveFileName(
            this, "Save Profile", "", "JSON Files (*.json)"
        );
        if (filepath.isEmpty()) return;
        m_currentProfilePath = filepath;
    }
    
    // TODO: Сериализовать m_currentValues в JSON и сохранить
    
    statusBar()->showMessage("Profile saved");
}

void MainWindow::loadProfile()
{
    // TODO: Загрузить профиль и обновить значения
    
    QString filepath = QFileDialog::getOpenFileName(
        this, "Open Profile", "", "JSON Files (*.json)"
    );
    
    if (filepath.isEmpty()) return;
    
    // TODO: Загрузить JSON и обновить m_currentValues
    
    statusBar()->showMessage("Profile loaded: " + filepath);
}

void MainWindow::resetAllToDefault()
{
    // TODO: Сбросить все значения к default
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        this, "Reset All",
        "Reset all parameters to default values?",
        QMessageBox::Yes | QMessageBox::No
    );
    
    if (reply == QMessageBox::Yes) {
        // TODO: Сбросить значения
        // m_currentValues.clear();
        // m_modifiedValues.clear();
        // m_parameterModel->setValues(m_currentValues);
        
        statusBar()->showMessage("All parameters reset to default");
    }
}

void MainWindow::onParameterChanged(const QString& name, const QVariant& value)
{
    // TODO: Обработать изменение параметра
    //
    // 1. Обновить m_currentValues
    // 2. Добавить в m_modifiedValues если отличается от default
    // 3. Обновить статус
    
    m_currentValues[name] = value;
    m_modifiedValues[name] = value;
    
    statusBar()->showMessage("Modified: " + name);
}

void MainWindow::onCategorySelected(const QModelIndex& index)
{
    // TODO: Показать параметры выбранной категории
    //
    // 1. Получить имя группы/подгруппы из модели
    // 2. Вызвать showParametersForCategory()
    
    Q_UNUSED(index);
}

void MainWindow::onSearchTextChanged(const QString& text)
{
    // TODO: Фильтровать параметры по тексту
    //
    // Используйте m_filterModel->setFilterRegularExpression()
    
    Q_UNUSED(text);
}

void MainWindow::onParameterSelected(const QModelIndex& index)
{
    // TODO: Показать описание выбранного параметра
    
    Q_UNUSED(index);
}

void MainWindow::populateCategories()
{
    // TODO: Заполнить дерево категорий из m_schema
    //
    // Для каждой группы создать QStandardItem
    // Добавить подгруппы как дочерние элементы
    
    m_categoryModel->clear();
    
    // for (const auto& group : m_schema.groups) {
    //     auto* groupItem = new QStandardItem(group.name);
    //     for (const auto& subgroup : group.subgroups) {
    //         auto* subItem = new QStandardItem(subgroup.name);
    //         groupItem->appendRow(subItem);
    //     }
    //     m_categoryModel->appendRow(groupItem);
    // }
}

void MainWindow::showParametersForCategory(const QString& group, const QString& subgroup)
{
    // TODO: Показать параметры категории в таблице
    
    Q_UNUSED(group);
    Q_UNUSED(subgroup);
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

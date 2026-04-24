#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include "parameter.h"

ParameterSchema ParameterSchema::load(const QString& filepath)
{
    ParameterSchema schema;

    QFile file(filepath);
    if (!file.open(QIODevice::ReadOnly)) {
        qWarning() << "Cannot open schema file:" << filepath;
        return schema;
    }

    QByteArray data = file.readAll();
    QJsonDocument document = QJsonDocument::fromJson(data);

    QJsonObject obj = document.object();
    
    schema.version = obj["version"].toString();
    schema.vehicle = obj["vehicle"].toString();

    QJsonArray groupsArray = obj["groups"].toArray();
    for (const QJsonValue& group : groupsArray) {
        QJsonObject groupObject = group.toObject();
        ParameterGroup parameterGroup;
        parameterGroup.name = groupObject["name"].toString();
        parameterGroup.description = groupObject["description"].toString();
        QJsonArray subgroupArray = groupObject["subgroups"].toArray();
        
        for (const QJsonValue& subgroup : subgroupArray) {
            QJsonObject subgroupObject = subgroup.toObject();
            ParameterSubgroup parameterSubgroup;
            parameterSubgroup.name = subgroupObject["name"].toString();
            QJsonArray parameterArray = subgroupObject["parameters"].toArray();

            for (const QJsonValue& parameterVal : parameterArray) {
                QJsonObject parameterObject = parameterVal.toObject();
                Parameter parameter;
                parameter.name  = parameterObject["name"].toString();
                parameter.displayName = parameterObject["displayName"].toString();
                parameter.description = parameterObject["description"].toString();
                parameter.group = parameterGroup.name;
                parameter.subgroup = parameterSubgroup.name;

                QString typeStr = parameterObject["type"].toString();
                if (typeStr == "float") parameter.type = ParameterType::Float;
                else if (typeStr == "int") parameter.type = ParameterType::Int;
                else if (typeStr == "bool") parameter.type = ParameterType::Bool;
                else if (typeStr == "enum") parameter.type = ParameterType::Enum;
                else parameter.type = ParameterType::String;

                                // Числовые значения
                parameter.defaultValue = parameterObject["default"].toVariant();
                parameter.minValue = parameterObject["min"].toVariant();
                parameter.maxValue = parameterObject["max"].toVariant();
                parameter.increment = parameterObject["increment"].toDouble();
                parameter.units = parameterObject["units"].toString();
                
                // Парсинг enum значений (если есть)
                if (parameter.type == ParameterType::Enum && parameterObject.contains("values")) {
                    QJsonArray enumArray = parameterObject["values"].toArray();
                    for (const QJsonValue& enumVal : enumArray) {
                        QJsonObject enumObj = enumVal.toObject();
                        EnumValue ev;
                        ev.value = enumObj["value"].toInt();
                        ev.name = enumObj["name"].toString();
                        ev.description = enumObj["description"].toString();
                        parameter.enumValues.append(ev);
                    }
                }
                
                parameterSubgroup.parameters.append(parameter);
            }
        parameterGroup.subgroups.append(parameterSubgroup);
        }
        schema.groups.append(parameterGroup);
    }

    // qDebug() << "Version:" << schema.version;
    // qDebug() << "Vehicle:" << schema.vehicle;
    
    // for (const auto& group : schema.groups) {
    //     qDebug() << "\n[Group]" << group.name << "-" << group.description;
    //     for (const auto& subgroup : group.subgroups) {
    //         qDebug() << "  [Subgroup]" << subgroup.name;
    //         for (const auto& param : subgroup.parameters) {
    //             qDebug() << "    -" << param.name << "=" << param.defaultValue 
    //                      << "(" << param.displayName << ")";
    //         }
    //     }
    // }

    
    return schema;
}
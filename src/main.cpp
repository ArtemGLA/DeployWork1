#include <iostream>
#include <iomanip>
#include <limits>

using namespace std;

// Функция для ввода числа с проверкой диапазона от 1 до 100
int inputNumber(const string& prompt) {
    int number;
    while (true) {
        cout << prompt;
        cin >> number;
        
        // Проверка на корректный ввод (чтобы не ввели буквы или символы)
        if (cin.fail()) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "Ошибка! Введите целое число от 1 до 100." << endl;
        }
        // Проверка диапазона
        else if (number < 1 || number > 100) {
            cout << "Ошибка! Число должно быть от 1 до 100." << endl;
        }
        else {
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            return number;
        }
    }
}

// Функция для ввода матрицы с клавиатуры
void inputMatrix(int** matrix, int size, const string& name) {
    cout << "\nВведите элементы матрицы " << name << " (" << size << "x" << size << "):" << endl;
    cout << "Числа должны быть целыми от 1 до 100." << endl;
    
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            string prompt = "Элемент [" + to_string(i+1) + "][" + to_string(j+1) + "]: ";
            matrix[i][j] = inputNumber(prompt);
        }
    }
}

// Функция для вывода матрицы на экран
void printMatrix(int** matrix, int size, const string& name) {
    cout << "\nМатрица " << name << " (" << size << "x" << size << "):" << endl;
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            cout << setw(4) << matrix[i][j] << " ";
        }
        cout << endl;
    }
}

// Функция для вычисления среднего арифметического элементов на диагоналях
double calculateDiagonalAverage(int** matrix, int size) {
    int sum = 0;
    int count = 0;
    
    cout << "\nЭлементы на диагоналях матрицы " << size << "x" << size << ":" << endl;
    
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            // Проверка, находится ли элемент на главной или побочной диагонали
            if (i == j || i + j == size - 1) {
                cout << "matrix[" << i+1 << "][" << j+1 << "] = " << matrix[i][j] << endl;
                sum += matrix[i][j];
                count++;
            }
        }
    }
    
    cout << "Сумма элементов на диагоналях: " << sum << endl;
    cout << "Количество элементов на диагоналях: " << count << endl;
    
    return static_cast<double>(sum) / count;
}

// Функция для замены элементов вне диагоналей
void replaceNonDiagonalElements(int** matrix, int size, double average) {
    int replaced = 0;
    int avgInt = static_cast<int>(average); // Преобразуем среднее в целое для замены
    
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            // Если элемент не на главной и не на побочной диагонали
            if (i != j && i + j != size - 1) {
                matrix[i][j] = avgInt;
                replaced++;
            }
        }
    }
    
    cout << "Заменено элементов вне диагоналей: " << replaced << endl;
}

int main() {
    setlocale(LC_ALL, "Russian");
    
    cout << "=== Программа для обработки матриц ===" << endl;
    cout << "Все вводимые числа должны быть целыми от 1 до 100." << endl;
    
    // Создание матрицы A 5x5
    int sizeA = 5;
    int** matrixA = new int*[sizeA];
    for (int i = 0; i < sizeA; i++) {
        matrixA[i] = new int[sizeA];
    }
    
    // Ввод матрицы A
    inputMatrix(matrixA, sizeA, "A");
    printMatrix(matrixA, sizeA, "A (до обработки)");
    
    // Создание матрицы C 6x6
    int sizeC = 6;
    int** matrixC = new int*[sizeC];
    for (int i = 0; i < sizeC; i++) {
        matrixC[i] = new int[sizeC];
    }
    
    // Ввод матрицы C
    inputMatrix(matrixC, sizeC, "C");
    printMatrix(matrixC, sizeC, "C (до обработки)");
    
    // Вычисление среднего арифметического для диагоналей обеих матриц
    // Вычисление среднего арифметического для диагоналей обеих матриц
    cout << "\n=== Вычисление среднего арифметического диагоналей ===" << endl;

    // Находим сумму и количество элементов на диагоналях матрицы A
    int sumA = 0, countA = 0;
    for (int i = 0; i < sizeA; i++) {
        for (int j = 0; j < sizeA; j++) {
            if (i == j || i + j == sizeA - 1) {
                sumA += matrixA[i][j];
                countA++;
            }
        }
    }

    // Находим сумму и количество элементов на диагоналях матрицы C
    int sumC = 0, countC = 0;
    for (int i = 0; i < sizeC; i++) {
        for (int j = 0; j < sizeC; j++) {
            if (i == j || i + j == sizeC - 1) {
                sumC += matrixC[i][j];
                countC++;
            }
        }
    }

    // Общее среднее арифметическое всех диагональных элементов
    int totalSum = sumA + sumC;
    int totalCount = countA + countC;
    double totalAverage = static_cast<double>(totalSum) / totalCount;

    cout << "Сумма элементов на диагоналях матрицы A: " << sumA << " (количество: " << countA << ")" << endl;
    cout << "Сумма элементов на диагоналях матрицы C: " << sumC << " (количество: " << countC << ")" << endl;
    cout << "Общая сумма: " << totalSum << ", общее количество: " << totalCount << endl;
    cout << "Общее среднее арифметическое: " << fixed << setprecision(2) << totalAverage << endl;
    
    // Замена элементов вне диагоналей общим средним
    cout << "\n=== Замена элементов вне диагоналей ===" << endl;
    cout << "Замена элементов матрицы A:" << endl;
    replaceNonDiagonalElements(matrixA, sizeA, totalAverage);
    
    cout << "\nЗамена элементов матрицы C:" << endl;
    replaceNonDiagonalElements(matrixC, sizeC, totalAverage);
    
    // Вывод обработанных матриц
    printMatrix(matrixA, sizeA, "A (после обработки)");
    printMatrix(matrixC, sizeC, "C (после обработки)");
    
    // Освобождение памяти
    for (int i = 0; i < sizeA; i++) {
        delete[] matrixA[i];
    }
    delete[] matrixA;
    
    for (int i = 0; i < sizeC; i++) {
        delete[] matrixC[i];
    }
    delete[] matrixC;
    
    cout << "\nПрограмма завершена." << endl;
    
    return 0;
}

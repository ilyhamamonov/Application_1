from flask import Flask, render_template, request, Markup
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error
import io
import base64


conn = mysql.connector.connect(host='localhost',
                               database='python_mysql',
                               user='root',
                               password='root') # Подключение к БД

#--------------------------------------- Сайт

app = Flask(__name__)

# Главная страница
@app.route('/index.html')
def index_p():
    return render_template('index.html')

# Добавление предмета
@app.route('/add_lesson.html', methods=['GET', 'POST'])
def add_lesson_p():
    if request.method == "POST":
        name_lesson = request.form['Lesson']
        return add_lesson(cursor, name_lesson)        
    return render_template('add_lesson.html')

# Добавление ученика
@app.route('/add_student.html', methods=['GET', 'POST'])
def add_student_p():
    if request.method == "POST":
        name_student = request.form['Name']
        name_lesson = request.form['Lesson']
        return add_student(cursor, name_lesson, name_student)
    return render_template('add_student.html')

# Добавление оценки заданому ученику по заданому предмету за заданную дату
@app.route('/add_grade.html', methods=['GET', 'POST'])
def add_grade_p():
    if request.method == "POST":
        name_lesson = request.form['Lesson']
        name_student = request.form['Name']
        date = request.form['Date']
        grade = request.form['Grade']
        return add_grade(cursor, name_lesson, name_student, date, grade)
    return render_template('add_grade.html')

# Просмотр оценок ученика по заданному предмету за заданный диапазон дат
@app.route('/look_grades.html', methods=['GET', 'POST'])
def look_grades_p():
    if request.method == "POST":
        name_lesson = str(request.form['Lesson'])
        name = str(request.form['Name'])        
        date1 = int(request.form['Date1'])
        date2 = int(request.form['Date2'])
        return look_grades(name_lesson, name, date1, date2)
    return render_template('look_grades.html')

# Построение графика средней оценки по предмету за заданый период.
@app.route('/graph.html', methods=['GET', 'POST'])
def graph_p():
    if request.method == "POST":
        name_lesson = str(request.form['Lesson'])
        name = str(request.form['Name'])        
        date1 = int(request.form['Date1'])
        date2 = int(request.form['Date2'])
        return graph(name_lesson, name, date1, date2)
    return render_template('graph.html')

# Вывод всей таблицы (для удобства)
@app.route('/show_tables.html', methods=['GET', 'POST'])
def show_tables_p():  
    if request.method == "POST":
        name_lesson = str(request.form['Lesson'])
        return show_tables(name_lesson)
    return render_template('show_tables.html')

#--------------------------------------- Функции программы

# Подлючение к БД MySQL
def connect(conn):
    try:
        if conn.is_connected():
            print('Connected to MySQL database')
    except Error as e:
        print(e)
    pass

# Отключение от БД MySQL
def disconnect(conn):
    conn.close()
    print('Disconnected from MySQL database')
    pass

# Добавление предмета
def add_lesson(cursor, name_lesson):
    try:    # Проверка на существование предмета
        cursor.execute('create table ' + name_lesson + ' (name char(30), grade int(5), date int(31))')
        return 'Done! <br><a href="/index.html">Back to index.html</a>'
    except Error as e:
        return str(e)+'<br><a href="/index.html">Back to index.html</a>'
    pass

# Добавление ученика
def add_student(cursor, name_lesson, name_student):
    
    day = 5 # Количество дней в месяце

    try:
        for i in range(5):
            cursor.execute('insert into ' + name_lesson + ' (name, grade, date) values ("' + name_student + '", NULL, ' + str(i+1) + ')')   # Добавление ученика
        conn.commit()   # Обновление данных в таблице
        return 'Done! <br><a href="/index.html">Back to index.html</a>'
    except Error as e:
        return str(e)+'<br><a href="/index.html">Back to index.html</a>'
    pass

# Добавление оценки заданому ученику по заданому предмету за заданную дату
def add_grade(cursor, name_lesson, name_student, date, grade):
    try:
        cursor.execute('update ' + name_lesson + ' set grade = ' + str(grade) + ' where (name = "' + name_student + '" and date = ' + str(date) + ')')  # Добавление оценки
        conn.commit()   # Обновление данных в таблице
        return 'Done! <br><a href="/index.html">Back to index.html</a>'    
    except Error as e:
        return(str(e)+'<br><a href="/index.html">Back to index.html</a>')
    pass

# Просмотр оценок ученика по заданному предмету за заданный диапазон дат
def look_grades(name_lesson, name, date1, date2):
    try:    
        cursor.execute('SELECT * FROM python_mysql.' + name_lesson)
    except Error as e:
        return(str(e)+'<br><a href="/index.html">Back to index.html</a>')   # Проверка на существование предмета     
    aa = 'Число / Имя / Оценка <br>'
    for (name1, name2, name3) in cursor:    # Вся таблица
        if (date1 <= name3 <= date2 and name1 == name): # Ограничение по заданным датам и совпадении по заданному имени
            if name2 != None:   # Выделение только строк с оценками
                aa = aa + str(name3) + ' ' + str(name1) + ' ' + str(name2) + '<br>'
    return aa+'<br><a href="/index.html">Back to index.html</a>'

# Построение графика средней оценки по предмету за заданый период.
def graph(name_lesson, name, date1, date2):  
    try:    
        cursor.execute('SELECT * FROM python_mysql.' + name_lesson)
    except Error as e:
        return(str(e)+'<br><a href="/index.html">Back to index.html</a>')   # Проверка на существование предмета

    oc = 0  # Начальные значения для графика
    sroc = 0    # Средняя оценка
    koloc = 0   # Количество оценок
    den = date1 # Номер дня
    xx=[]   # Ось X
    yy=[]   # Ось Y

    for (name1, name2, name3) in cursor:    # Формирование массива данных для осей графика
        if (date1 <= name3 <= date2 and name1 == name): # Ограничение по заданным датам и совпадении по заданному имени
            if name2 != None:
                oc = oc+name2
                koloc = koloc +1
                sroc = oc/koloc
                xx.append(den)
                yy.append(sroc)
            else:            
                xx.append(den)
                yy.append(sroc)
            den = den+1
        
    plt.bar(xx,yy, width = 1, align='edge') # Построение графика в виде столбцов
    graph = io.BytesIO()
    plt.savefig(graph, format='png')    # Запись графика в динамическую память
    plt.clf()   # Удаление фигуры после сохранения в динамическую память
    plot = base64.b64encode(graph.getvalue()).decode()  # Декодирование для html
    return str('<img src="data:image/png;base64,{}">'.format(plot))+'<br><a href="/index.html">Back to index.html</a>'

# Вывод всей таблицы (для удобства)
def show_tables(name_lesson):    
    try:    # Проверка на существование предмета
        cursor.execute('SELECT * FROM python_mysql.' + name_lesson)
    except Error as e:
        return(str(e)+'<br><a href="/index.html">Back to index.html</a>')

    aa = 'Число / Имя / Оценка <br>'
    for (name1, name2, name3) in cursor:
        if name2 == None:
            aa = aa + str(name3) + ' ' + str(name1) + '<br>'
        else:
            aa = aa + str(name3) + ' ' + str(name1) + ' ' + str(name2) + '<br>'
    return aa+'<br><a href="/index.html">Back to index.html</a>'
    
if __name__ == '__main__':
    cursor = conn.cursor()
    
    # Функции
    connect(conn)   # Подключение к БД
    app.run()   # Запуск сервера
    disconnect(conn)    # Отключение от БД
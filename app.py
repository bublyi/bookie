from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'mybooksecret123'

def init_db():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'To Read'
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        status = request.form['status']
        
        if not title or not author:
            flash('Title and Author are required!')
            return render_template('add_book.html')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author, status) VALUES (?, ?, ?)', 
                     (title, author, status))
        conn.commit()
        conn.close()
        
        flash('Book added successfully!')
        return redirect(url_for('index'))
    
    return render_template('add_book.html')

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if book is None:
        flash('Book not found!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        status = request.form['status']
        
        if not title or not author:
            flash('Title and Author are required!')
            return render_template('edit_book.html', book=book)
        
        conn.execute('UPDATE books SET title = ?, author = ?, status = ? WHERE id = ?', 
                     (title, author, status, book_id))
        conn.commit()
        conn.close()
        
        flash('Book updated successfully!')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    flash('Book deleted!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
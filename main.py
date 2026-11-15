import flet as ft
import sqlite3
from datetime import date, timedelta

def init_db():
    conn = sqlite3.connect('english_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL, meaning TEXT,
            proficiency INTEGER DEFAULT 0, next_review TEXT, add_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, add_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, source TEXT,
            sort_order INTEGER DEFAULT 0, add_date TEXT
        )
    ''')
    cursor.execute("UPDATE words SET next_review = date('now') WHERE next_review IS NULL")
    conn.commit()
    conn.close()

init_db()

def main(page: ft.Page):
    page.title = "我的英语学习软件"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    def word_page():
        page.controls.clear() 
        top_bar = ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: main_menu()), ft.Text("整理生词", size=24, weight=ft.FontWeight.BOLD)])
        word_input = ft.TextField(label="输入英语单词", width=300)
        meaning_input = ft.TextField(label="输入中文释义", width=300)
        word_list_view = ft.Column(width=300)

        def load_words():
            word_list_view.controls.clear()
            conn = sqlite3.connect('english_app.db')
            rows = conn.cursor().execute("SELECT id, word, meaning FROM words ORDER BY id DESC").fetchall()
            conn.close()
            if not rows: word_list_view.controls.append(ft.Text("暂无生词，快添加吧！", color="grey"))
            for w_id, w, m in rows: 
                def delete_word(e, target_id=w_id):
                    conn = sqlite3.connect('english_app.db')
                    conn.cursor().execute("DELETE FROM words WHERE id = ?", (target_id,))
                    conn.commit(); conn.close()
                    load_words()
                row = ft.Row([
                    ft.Text(f"🔹 {w} : {m}", size=16, expand=True),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", icon_size=20, on_click=delete_word)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                word_list_view.controls.append(row)
            page.update()

        def save_word(e):
            if word_input.value == "" or meaning_input.value == "": return
            conn = sqlite3.connect('english_app.db')
            conn.cursor().execute("INSERT INTO words (word, meaning, proficiency, next_review, add_date) VALUES (?, ?, 0, date('now'), date('now'))", (word_input.value, meaning_input.value))
            conn.commit(); conn.close()
            word_input.value = ""; meaning_input.value = ""
            load_words()

        page.add(top_bar, word_input, meaning_input, ft.Button("保存生词", width=300, on_click=save_word), ft.Divider(), ft.Text("我的生词本：", size=18, weight=ft.FontWeight.BOLD), word_list_view)
        load_words()

    def article_page():
        page.controls.clear()
        top_bar = ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: main_menu()), ft.Text("录入美文", size=24, weight=ft.FontWeight.BOLD)])
        title_input = ft.TextField(label="文章标题（可选）", width=300)
        content_input = ft.TextField(label="文章正文", multiline=True, min_lines=5, max_lines=10, width=300)
        article_list = ft.Column(width=300)

        def load_articles():
            article_list.controls.clear()
            conn = sqlite3.connect('english_app.db')
            rows = conn.cursor().execute("SELECT id, title, content FROM articles ORDER BY id DESC").fetchall()
            conn.close()
            if not rows: article_list.controls.append(ft.Text("暂无文章，快添加吧！", color="grey"))
            for a_id, title, content in rows:
                t = title if title else "无标题"
                def delete_article(e, target_id=a_id):
                    conn = sqlite3.connect('english_app.db')
                    conn.cursor().execute("DELETE FROM articles WHERE id = ?", (target_id,))
                    conn.commit(); conn.close()
                    load_articles()
                row = ft.Row([
                    ft.Text(f"📄 {t} ({content[:10]}...)", size=14, expand=True),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", icon_size=20, on_click=delete_article)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                article_list.controls.append(row)
            page.update()

        def save_article(e):
            if content_input.value == "": return
            conn = sqlite3.connect('english_app.db')
            conn.cursor().execute("INSERT INTO articles (title, content, add_date) VALUES (?, ?, date('now'))", (title_input.value, content_input.value))
            conn.commit(); conn.close()
            title_input.value = ""; content_input.value = ""
            load_articles()

        page.add(top_bar, title_input, content_input, ft.Button("保存文章", width=300, on_click=save_article), ft.Divider(), article_list)
        load_articles()

    def sentence_page():
        page.controls.clear()
        top_bar = ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: main_menu()), ft.Text("摘录美句", size=24, weight=ft.FontWeight.BOLD)])
        text_input = ft.TextField(label="输入美句", width=300)
        source_input = ft.TextField(label="出处/备注（可选）", width=300)
        sentence_list = ft.Column(width=300)

        def load_sentences():
            sentence_list.controls.clear()
            conn = sqlite3.connect('english_app.db')
            rows = conn.cursor().execute("SELECT id, text, source, sort_order FROM sentences ORDER BY sort_order ASC, id ASC").fetchall()
            conn.close()
            
            for index, (s_id, text, source, order) in enumerate(rows):
                src = f" - {source}" if source else ""
                
                def move_up(e, idx=index):
                    if idx > 0:
                        conn = sqlite3.connect('english_app.db')
                        cursor = conn.cursor()
                        prev_id, prev_order = cursor.execute("SELECT id, sort_order FROM sentences ORDER BY sort_order ASC, id ASC LIMIT 1 OFFSET ?", (idx - 1,)).fetchone()
                        cursor.execute("UPDATE sentences SET sort_order = ? WHERE id = ?", (prev_order, s_id))
                        cursor.execute("UPDATE sentences SET sort_order = ? WHERE id = ?", (order, prev_id))
                        conn.commit(); conn.close()
                        load_sentences()

                def move_down(e, idx=index):
                    conn = sqlite3.connect('english_app.db')
                    next_row = conn.cursor().execute("SELECT id, sort_order FROM sentences ORDER BY sort_order ASC, id ASC LIMIT 1 OFFSET ?", (idx + 1,)).fetchone()
                    conn.close()
                    if next_row:
                        next_id, next_order = next_row
                        conn = sqlite3.connect('english_app.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE sentences SET sort_order = ? WHERE id = ?", (next_order, s_id))
                        cursor.execute("UPDATE sentences SET sort_order = ? WHERE id = ?", (order, next_id))
                        conn.commit(); conn.close()
                        load_sentences()

                def delete_sentence(e, target_id=s_id):
                    conn = sqlite3.connect('english_app.db')
                    conn.cursor().execute("DELETE FROM sentences WHERE id = ?", (target_id,))
                    conn.commit(); conn.close()
                    load_sentences()

                row_ui = ft.Row([
                    ft.Text(f"{index+1}. 💬 {text}{src}", size=14, expand=True),
                    ft.IconButton(icon=ft.Icons.ARROW_UPWARD, icon_size=16, on_click=move_up),
                    ft.IconButton(icon=ft.Icons.ARROW_DOWNWARD, icon_size=16, on_click=move_down),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", icon_size=16, on_click=delete_sentence)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                sentence_list.controls.append(row_ui)
            page.update()

        def save_sentence(e):
            if text_input.value == "": return
            conn = sqlite3.connect('english_app.db')
            max_order = conn.cursor().execute("SELECT COALESCE(MAX(sort_order), 0) FROM sentences").fetchone()[0]
            conn.cursor().execute("INSERT INTO sentences (text, source, sort_order, add_date) VALUES (?, ?, ?, date('now'))", (text_input.value, source_input.value, max_order + 1))
            conn.commit(); conn.close()
            text_input.value = ""; source_input.value = ""
            load_sentences()

        page.add(top_bar, text_input, source_input, ft.Button("保存美句", width=300, on_click=save_sentence), ft.Divider(), ft.Text("美句列表：", size=14, weight=ft.FontWeight.BOLD), sentence_list)
        load_sentences()

    def review_page():
        page.controls.clear()
        review_queue = []
        current_idx = [0]  
        
        conn = sqlite3.connect('english_app.db')
        today_str = date.today().isoformat()
        review_queue.extend(conn.cursor().execute("SELECT id, word, meaning, proficiency FROM words WHERE next_review <= ? ORDER BY next_review ASC", (today_str,)).fetchall())
        conn.close()

        top_bar = ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: main_menu()), ft.Text("今日复习排班", size=24, weight=ft.FontWeight.BOLD)])
        content_area = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

        def show_next_word():
            content_area.controls.clear()
            if current_idx[0] >= len(review_queue):
                content_area.controls.append(ft.Text("🎉 今天的复习任务已全部完成！", size=20, color="green"))
                content_area.controls.append(ft.Button("返回主菜单", on_click=lambda e: main_menu()))
            else:
                w_id, w, m, prof = review_queue[current_idx[0]]
                content_area.controls.append(ft.Text(f"进度：{current_idx[0] + 1} / {len(review_queue)}", size=14, color="grey"))
                content_area.controls.append(ft.Container(height=20))
                content_area.controls.append(ft.Text(f"{w}", size=36, weight=ft.FontWeight.BOLD, color="blue"))
                content_area.controls.append(ft.Text(f"释义：{m}", size=20))
                content_area.controls.append(ft.Container(height=50))

                def handle_review(is_known):
                    new_prof = prof + 1 if is_known else 0
                    intervals = {0: 1, 1: 2, 2: 4, 3: 7, 4: 15, 5: 30}
                    actual_prof = min(new_prof, 5)
                    days_to_add = intervals[actual_prof]
                    next_date = (date.today() + timedelta(days=days_to_add)).isoformat()
                    
                    conn = sqlite3.connect('english_app.db')
                    conn.cursor().execute("UPDATE words SET proficiency = ?, next_review = ? WHERE id = ?", (actual_prof, next_date, w_id))
                    conn.commit(); conn.close()
                    
                    current_idx[0] += 1  
                    show_next_word()
                    page.update()

                btn_known = ft.Button("认识 (+熟练度)", width=150, bgcolor="green", color="white", on_click=lambda e: handle_review(True))
                btn_unknown = ft.Button("不认识 (明天重学)", width=150, bgcolor="red", color="white", on_click=lambda e: handle_review(False))
                content_area.controls.append(ft.Row([btn_known, btn_unknown], alignment=ft.MainAxisAlignment.CENTER))
            page.update()

        page.add(top_bar, ft.Divider(), content_area)
        show_next_word()

    def main_menu():
        page.controls.clear()
        conn = sqlite3.connect('english_app.db')
        today_str = date.today().isoformat()
        due_count = conn.cursor().execute("SELECT COUNT(*) FROM words WHERE next_review <= ?", (today_str,)).fetchone()[0]
        conn.close()

        title = ft.Text("我的英语学习软件", size=28, weight=ft.FontWeight.BOLD, color="blue")
        subtitle = ft.Text("选择你想要进行的操作", size=16, color="grey")
        review_btn_text = f"⏰ 今日复习排班 ({due_count})" if due_count > 0 else "⏰ 今日复习排班"

        page.add(
            ft.Container(height=20), title, subtitle, ft.Container(height=20),
            ft.Button("📖 录入美文", width=300, height=50, on_click=lambda e: article_page()),
            ft.Button("✍️ 摘录美句", width=300, height=50, on_click=lambda e: sentence_page()),
            ft.Button("📚 整理生词", width=300, height=50, on_click=lambda e: word_page()),
            ft.Button(review_btn_text, width=300, height=50, bgcolor="blue", color="white", on_click=lambda e: review_page())
        )
        page.update()

    main_menu()

ft.run(main)

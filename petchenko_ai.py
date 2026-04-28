import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# --- Конфигурация ---
FAVORITES_FILE = "favorites.json"
GITHUB_API_URL = "https://api.github.com/users/"

# --- Функции логики ---

def load_favorites():
    """Загружает избранных пользователей из файла JSON."""
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_favorites(favorites):
    """Сохраняет список избранных пользователей в файл JSON."""
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=4)

def is_favorited(username):
    """Проверяет, есть ли пользователь в избранном."""
    favorites = load_favorites()
    return any(user.get('login') == username for user in favorites)

def add_to_favorites(user_data):
    """Добавляет пользователя в избранное, если его там еще нет."""
    favorites = load_favorites()
    if not is_favorited(user_data['login']):
        favorites.append(user_data)
        save_favorites(favorites)
        messagebox.showinfo("Успех", f"{user_data['login']} добавлен в избранное!")
    else:
        messagebox.showwarning("Дубликат", "Пользователь уже в избранном.")

# --- Функции для GUI ---

def search_user():
    """Обрабатывает нажатие кнопки поиска."""
    username = entry_username.get().strip()
    
    # 5. Проверка корректности ввода (поле не должно быть пустым)
    if not username:
        messagebox.showerror("Ошибка", "Поле поиска не может быть пустым.")
        return

    # Блокируем интерфейс на время запроса
    set_interface_state(False)
    result_text.set("Поиск...") # Очистка и статус загрузки

    try:
        response = requests.get(f"{GITHUB_API_URL}{username}")
        
        if response.status_code == 200:
            data = response.json()
            display_user_info(data)
        elif response.status_code == 404:
            display_user_info(None)
        else:
            result_text.set(f"Ошибка {response.status_code}: {response.reason}")
    except requests.RequestException as e:
        result_text.set(f"Ошибка сети: {e}")
    finally:
        # Разблокируем интерфейс после завершения запроса
        set_interface_state(True)

def display_user_info(user_data):
    """
    Отображает информацию о пользователе в виджете Text.
    Если user_data == None, выводит сообщение о том, что пользователь не найден.
    """
    text_result.config(state='normal')
    text_result.delete(1.0, tk.END)
    
    if user_data is None:
        result_text.set("Пользователь не найден.")
        text_result.insert(tk.END, "Пользователь с таким именем не существует на GitHub.")
    else:
        # Формируем красивую строку с данными
        info_text = (
            f"Имя: {user_data.get('name', 'Не указано')}\n"
            f"Логин: {user_data.get('login')}\n"
            f"Био: {user_data.get('bio', 'Нет биографии')}\n"
            f"Публичные репозитории: {user_data.get('public_repos', 0)}\n"
            f"Подписчики: {user_data.get('followers', 0)}\n"
            f"Подписки: {user_data.get('following', 0)}\n"
            f"URL: {user_data.get('html_url')}"
        )
        text_result.insert(tk.END, info_text)
        
        # 3. Добавляем возможность добавления в избранное
        btn_favorite.config(
            text="⭐ Добавить в избранное" if not is_favorited(user_data['login']) else "⭐ В избранном",
            state='normal',
            command=lambda u=user_data: add_to_favorites(u)
        )

    text_result.config(state='disabled')

def set_interface_state(is_active):
    """Блокирует или разблокирует элементы интерфейса."""
    state = 'normal' if is_active else 'disabled'
    entry_username.config(state=state)
    btn_search.config(state=state)

# --- Создание главного окна ---
root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("500x450")
root.resizable(False, False)

# Основной фрейм с отступами
main_frame = ttk.Frame(root, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

# 1. Поле ввода для поиска пользователя GitHub
label_username = ttk.Label(main_frame, text="Имя пользователя GitHub:")
label_username.grid(row=0, column=0, sticky=tk.W, pady=5)

entry_username = ttk.Entry(main_frame, width=40)
entry_username.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.EW)

btn_search = ttk.Button(main_frame, text="🔍 Найти", command=search_user)
btn_search.grid(row=1, column=2, padx=5)

# 2. Отображение результатов поиска в виде списка (в данном случае - в виджете Text)
result_text = tk.StringVar()
label_result = ttk.Label(main_frame, textvariable=result_text)
label_result.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

text_result = tk.Text(main_frame, height=12, width=55, wrap=tk.WORD, state='disabled')
text_result.grid(row=3, column=0, columnspan=3, pady=5)

# 3. Кнопка для добавления в избранное (изначально скрыта/неактивна)
btn_favorite = ttk.Button(main_frame, text="⭐ Добавить в избранное", state='disabled')
btn_favorite.grid(row=4, column=0, columnspan=3, pady=(15, 0))

# Запуск приложения
root.mainloop()

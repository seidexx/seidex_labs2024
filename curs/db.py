import sqlite3

class BotDB:

    def __init__(self, db_file):
        """Ініціалізація і з'єднання з БД"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Перевіряємо чи є користувач у базі"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Отримуємо id користувача у базі з його user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        """Додаємо користувача у базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_record(self, user_id, operation, value):
        """Створюємо запис про прибуток/витрату"""
        self.cursor.execute("INSERT INTO `records` (`users_id`, `operation`, `value`) VALUES (?, ?, ?)",
            (self.get_user_id(user_id),
            operation == "+",
            value))
        return self.conn.commit()

    def get_records(self, user_id, within = "all"):
        """Отримуємо історію про прибутки/витрати відповідно до вказаного періоду"""

        if(within == "day"):
            result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        elif(within == "week"):
            result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        elif(within == "month"):
            result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        else:
            result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? ORDER BY `date`",
                (self.get_user_id(user_id),))

        return result.fetchall()

    def give_id_list(self, user_id):
        """Передаємо список id усіх операцій у БД по даному користувачу"""
        result = self.cursor.execute("SELECT `id` FROM `records` WHERE `users_id` = ? ORDER BY `date`",
                                     (self.get_user_id(user_id),))
        return result.fetchall()

    def del_record(self, user_id, id):
        """Видаляємо запис у БД по id, якщо він належить даному користувачу"""
        self.cursor.execute('DELETE FROM `records` WHERE `id` = ? AND `users_id` = ?',
                            (id, (self.get_user_id(user_id))))
        return self.conn.commit()

    def close(self):
        """Закриваємо з'єднання з БД"""
        self.conn.close()
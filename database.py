import sqlite3
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_name='my.db'):
        self.db_name = db_name
        self.conn = None
        self.connect()
        self.create_table()

    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row  # 使返回的行像字典一样访问

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def create_table(self):
        """创建用户表"""
        query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.execute_query(query)
        self.conn.commit()

    def execute_query(self, query: str, params=()) -> sqlite3.Cursor:
        """执行SQL查询"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    # 用户认证相关方法
    # 用户认证相关方法
    def validate_user(self, username: str, password: str) -> bool:
        """验证用户凭据"""
        # 将用户名和密码转换为小写
        username = username.lower()
        password = password.lower()

        query = 'SELECT id FROM users WHERE LOWER(username)=? AND LOWER(password)=?'
        cursor = self.execute_query(query, (username, password))
        return cursor.fetchone() is not None

    def register_user(self, username: str, password: str) -> bool:
        """注册新用户"""
        try:
            self.execute_query(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    # 用户管理CRUD方法
    def get_all_users(self) -> List[sqlite3.Row]:
        """获取所有用户"""
        cursor = self.execute_query('SELECT * FROM users ORDER BY id')
        return cursor.fetchall()

    def search_users(self, keyword: str) -> List[sqlite3.Row]:
        """搜索用户"""
        cursor = self.execute_query(
            'SELECT * FROM users WHERE username LIKE ? ORDER BY id',
            (f'%{keyword}%',)
        )
        return cursor.fetchall()

    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        """根据ID获取用户"""
        cursor = self.execute_query('SELECT * FROM users WHERE id=?', (user_id,))
        return cursor.fetchone()

    def add_user(self, username: str, password: str) -> Tuple[bool, str]:
        """添加用户"""
        try:
            self.execute_query(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.conn.commit()
            return True, "用户添加成功"
        except sqlite3.IntegrityError:
            return False, "用户名已存在"
        except Exception as e:
            return False, f"添加用户失败: {str(e)}"

    def update_user(self, user_id: int, username: str, password: Optional[str] = None) -> Tuple[bool, str]:
        """更新用户信息"""
        try:
            if password:
                self.execute_query(
                    'UPDATE users SET username=?, password=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                    (username, password, user_id)
                )
            else:
                self.execute_query(
                    'UPDATE users SET username=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                    (username, user_id)
                )
            self.conn.commit()
            return True, "用户信息更新成功"
        except sqlite3.IntegrityError:
            return False, "用户名已存在"
        except Exception as e:
            return False, f"更新用户失败: {str(e)}"

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """删除用户"""
        try:
            self.execute_query('DELETE FROM users WHERE id=?', (user_id,))
            self.conn.commit()
            return True, "用户删除成功"
        except Exception as e:
            return False, f"删除用户失败: {str(e)}"

    def reset_password(self, user_id: int, new_password: str) -> Tuple[bool, str]:
        """重置用户密码"""
        try:
            self.execute_query(
                'UPDATE users SET password=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                (new_password, user_id)
            )
            self.conn.commit()
            return True, "密码重置成功"
        except Exception as e:
            return False, f"重置密码失败: {str(e)}"
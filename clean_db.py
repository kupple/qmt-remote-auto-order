import os
import sqlite3
from pathlib import Path

def clean_database():
    """清理数据库文件，保留空的数据库结构"""
    db_path = Path("static/db/base.db")
    
    if not db_path.exists():
        print(f"数据库文件 {db_path} 不存在")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # 删除所有表的数据，但保留 alembic_version 表
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence' and table_name != 'alembic_version':  # 不删除序列表和版本表
                cursor.execute(f"DELETE FROM {table_name}")
        
        # 提交事务
        conn.commit()
        print("数据库已成功清空")
    except Exception as e:
        print(f"清理数据库时出错: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clean_database()

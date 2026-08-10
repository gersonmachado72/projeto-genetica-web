import os

class Config:
    SECRET_KEY = 'genetica-secret-key-2026'
    
    # Configurações do MySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'luck'           
    MYSQL_PASSWORD = '0397154#_!54179330_#!wsx_yhn#!'  
    MYSQL_DB = 'genetica_db'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Configurações de upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'txt', 'fasta', 'fa'}
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = 3600

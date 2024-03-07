import os

class path:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Diretório pai do arquivo config.py
    data     = os.path.join(base_dir, 'data')
    yaml     = os.path.join(data, 'yml')
    sql      = os.path.join(data, 'sql')
    icon     = os.path.join(base_dir, 'icon')
    ui       = os.path.join(base_dir, 'ui')
    locales  = os.path.join(base_dir, 'locales')
    logos    = os.path.join(base_dir, 'logos')

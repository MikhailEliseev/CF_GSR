#!/usr/bin/env python3
"""
Создает standalone версию module_vacancies.html без зависимости от base.html
"""

# Читаем оригинальный шаблон
with open('templates/module_vacancies.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Убираем Jinja2 блоки
lines = content.split('\n')
filtered_lines = []
skip_line = False

for line in lines:
    # Пропускаем все строки с Jinja2 блоками
    if '{% extends' in line:
        continue
    if '{% block' in line:
        continue
    if '{% endblock' in line:
        continue
    filtered_lines.append(line)

content = '\n'.join(filtered_lines)

# Создаем полный HTML документ
html_template = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Модуль Вакансий - GSR Content Factory</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- GSR Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Russo+One&family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <!-- GSR Corporate Styles -->
    <style>
        :root {{
            --gsr-primary: #004027;
            --gsr-secondary: #396225;
            --gsr-accent: #279134;
            --gsr-light: #F2F2EB;
            --gsr-orange: #EB8000;
            --font-heading: 'Russo One', sans-serif;
            --font-body: 'Inter', sans-serif;
        }}
        
        body {{
            font-family: var(--font-body);
            background: var(--gsr-light);
            color: #333;
        }}
        
        .gsr-bg-primary {{ background: var(--gsr-primary) !important; }}
        .gsr-bg-accent {{ background: var(--gsr-accent) !important; }}
        .gsr-text-primary {{ color: var(--gsr-primary) !important; }}
        .gsr-heading {{ font-family: var(--font-heading); }}
        .btn-gsr-accent {{
            background: var(--gsr-accent);
            border-color: var(--gsr-accent);
            color: white;
        }}
        .btn-gsr-accent:hover {{
            background: var(--gsr-secondary);
            border-color: var(--gsr-secondary);
            color: white;
        }}
    </style>

{content}

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

# Сохраняем
with open('templates/module_vacancies_full.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ Создан standalone шаблон: templates/module_vacancies_full.html")


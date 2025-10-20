# 🔧 Настройка Apify Instagram Reels Scraper

## 📋 **Актор ID:** `xMc5Ga1oCONPmWJIa`

Согласно документации и анализу ссылки [https://console.apify.com/actors/xMc5Ga1oCONPmWJIa](https://console.apify.com/actors/xMc5Ga1oCONPmWJIa), это специализированный Instagram Reels Scraper.

---

## 🔧 **Обновленные настройки в системе:**

### **✅ Исправления применены:**

1. **🎯 Актор ID:** Изменен на указанный вами `xMc5Ga1oCONPmWJIa`

2. **📝 Входные параметры обновлены:**
```json
{
  "profiles": ["username"],
  "resultsLimit": 20,
  "resultsType": "posts", 
  "addParentData": false,
  "includeHasStoryHighlight": false
}
```

3. **🔒 SSL исправления:** Добавлены для ElevenLabs и HeyGen API

4. **🚫 Демо-данные:** Полностью удалены

---

## 🎯 **Что нужно проверить в Apify Console:**

### **1. Проверьте актор в консоли:**
- Откройте: https://console.apify.com/actors/xMc5Ga1oCONPmWJIa
- Убедитесь, что актор доступен для вашего аккаунта
- Проверьте лимиты и права доступа

### **2. Тестовый запуск:**
В Apify Console попробуйте запустить актор с параметрами:
```json
{
  "profiles": ["garyvee"],
  "resultsLimit": 5,
  "resultsType": "posts"
}
```

### **3. Проверьте баланс:**
- В Apify Console → Settings → Billing
- Убедитесь, что есть доступные кредиты

---

## 🚀 **Альтернативные акторы (если основной не работает):**

### **Instagram Post Scraper (zuzka/instagram-scraper):**
```json
{
  "usernames": ["username"],
  "resultsType": "posts",
  "resultsLimit": 20,
  "searchType": "user"
}
```

### **Instagram Scraper & Posts Downloader:**
```json
{
  "usernames": ["username"], 
  "resultsLimit": 20,
  "includeHashtags": true,
  "includeLocation": true
}
```

---

## 🔍 **Диагностика проблем:**

### **Если получаете ошибки:**

1. **Проверьте актор:** Убедитесь, что `xMc5Ga1oCONPmWJIa` доступен в вашей консоли

2. **Проверьте права:** Возможно нужна подписка или специальные права

3. **Проверьте формат:** Актор может требовать другие параметры входа

4. **Проверьте лимиты:** Instagram может блокировать запросы

---

## 💡 **Рекомендации:**

1. **📊 Начните с 1-2 профилей** для тестирования
2. **⏱ Используйте небольшие лимиты** (5-10 постов)
3. **🔄 Добавьте задержки** между запросами
4. **📈 Отслеживайте использование кредитов**

---

## 🎯 **Следующие шаги:**

1. **Проверьте актор в консоли** Apify
2. **Протестируйте** с одним профилем
3. **Обновите настройки** при необходимости
4. **Добавьте OpenAI Assistant ID** для переписывания

---

**📱 Обновите страницу и протестируйте с обновленными настройками!**

# SD_test_task


Postgre запускается через docker-compose командой:
    
    docker-compose up -d

зависимости лежат в requirements.txt, установка:

    pip install -r requirements.txt

старт приложения:

    flask --app main init-db
    python main.py


Создать товар:

    curl -X POST \
    http://localhost:5000/products \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_TOKEN" \
    -d '{
            "name": "phone",       
            "price": "10500"    
    }'

Изменить товар:
  
    curl -X PUT \
    http://localhost:5000/products/1 \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_TOKEN" \
    -d '{
	"name": "iphone",
	"price": "100000"
    }'

Добавить в корзину:

    curl -X POST \
    http://localhost:5000/carts \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_TOKEN" \
    -d '{
        "product_id": "1",
        "quantity": "1"
    }'

Изменить количество товара в корзине:

    curl -X PUT \
    http://localhost:5000/carts/<cart_id> \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_TOKEN" \
    -d '{
        "quantity": "new_quantity"
    }'

Удалить из корзины:

    curl -X DELETE \
    http://localhost:5000/carts/1 \
    -H "Authorization: Bearer $API_TOKEN"

Удалить товар из магазина:

    curl -X DELETE \
    http://localhost:5000/products/1 \
    -H "Authorization: Bearer $API_TOKEN"



## Настройка безопасности

Используйте Python 3.12+ и virtualenv. До импорта приложения задайте DATABASE_URL
и случайный API_TOKEN длиной минимум 32 символа. Все маршруты требуют заголовок
`Authorization: Bearer <API_TOKEN>`; токен общий для доверенных клиентов этой
учебной системы, персональные корзины/роли пользователей здесь не реализованы.
Не передавайте токен в query string. При публичном запуске используйте HTTPS и
production WSGI server, например `gunicorn main:app --bind 127.0.0.1:8000`,
за reverse proxy. Flask debugger отключён.

Создайте новые независимые значения вне checkout (права 600) или в secret store:

```bash
export POSTGRES_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export API_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
# Для новой локальной БД; сгенерированный пароль URL-safe.
export DATABASE_URL="postgresql://user_postgres:${POSTGRES_PASSWORD}@127.0.0.1:5432/db_store"
docker compose up -d
flask --app main init-db
```

Django/Flask не загружают `.env` автоматически: обеспечьте передачу переменных
окружения через supervisor/хостинг. PostgreSQL слушает только localhost.
Существующую БД сначала сохраните: изменение POSTGRES_PASSWORD в Compose не
меняет пароль существующего PostgreSQL пользователя. В доверенном `psql`
выполните `\password user_postgres`, затем синхронно обновите DATABASE_URL и
POSTGRES_PASSWORD и перезапустите приложение. Не удаляйте volume ради смены
пароля и не меняйте major-версию PostgreSQL без отдельной миграции. Образ
`postgres` для существующего сервера нужно закрепить на уже установленной
поддерживаемой major-версии после инвентаризации: автоматическая смена опасна
для существующих данных. Проверьте firewall/security group: внешний 5432 закрыт.

Проверка авторизации и CRUD: `python -m unittest discover -s tests`.

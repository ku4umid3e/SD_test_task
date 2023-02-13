# SD_test_task


Postgre запускается через docker-compose командой:
    
    docker-compose up -d

зависимости лежат в requirements.txt, установка:

    pip install -r requirements.txt

старт приложения:

    python main.py


Создать товар:

    curl -X POST \
    http://localhost:5000/products \
    -H 'Content-Type: application/json' \
    -d '{
            "name": "phone",       
            "price": "10500"    
    }'

Изменить товар:
  
    curl -X PUT \
    http://localhost:5000/products/1 \
    -H 'Content-Type: application/json' \
    -d '{
	"name": "iphone",
	"price": "100000"
    }'

Добавить в корзину:

    curl -X POST \
    http://localhost:5000/carts \
    -H 'Content-Type: application/json' \
    -d '{
        "product_id": "1",
        "quantity": "1"
    }'

Изменить количество товара в корзине:

    curl -X PUT \
    http://localhost:5000/carts/<cart_id> \
    -H 'Content-Type: application/json' \
    -d '{
        "quantity": "new_quantity"
    }'

Удалить из корзины:

    curl -X DELETE \
    http://localhost:5000/carts/1

Удалить товар из магазина:

    curl -X DELETE \
    http://localhost:5000/products/1



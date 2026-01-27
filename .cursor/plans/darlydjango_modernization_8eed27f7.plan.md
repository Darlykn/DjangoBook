---
name: DarlyDjango modernization
overview: "Модернизация Django-магазина: обновление фронта на Tailwind+Vite без SPA, расширение фильтров/категорий, промокоды с админкой и endpoint-ами, а также UX-правка карточек и подготовка БД/суперюзера."
todos:
  - id: db-setup
    content: Определить стратегию БД (миграции vs пересоздание), сделать бэкап и создать суперюзера для админки.
    status: completed
  - id: vite-tailwind
    content: Добавить Vite+Tailwind сборку и подключить скомпилированные ассеты в Django `static/` и `base.html`.
    status: in_progress
  - id: filters-ui
    content: "Сделать блок фильтров на странице списка: перенести категории, добавить новые фильтры, унифицировать через query params."
    status: pending
  - id: promocodes
    content: Создать app `promocodes`, модель+миграции+админку и endpoint-ы, интегрировать применение в корзине и повторную валидацию при создании заказа.
    status: pending
  - id: clickable-cards
    content: Сделать всю карточку товара кликабельной в `product/list.html`, обновить стили/hover состояния.
    status: pending
  - id: smoke-test
    content: "Провести регресс-проверку: каталог, поиск/фильтры, корзина, промокод, создание заказа, админка."
    status: pending
isProject: false
---

## Контекст (что есть сейчас)

- **Django MVT, шаблоны**: фронт на Django templates (`django_shop/shop/templates/...`), Bootstrap CDN.
- **БД**: SQLite (`django_shop/django_shop/settings.py`, `db.sqlite3`).
- **Категории**: `shop.Category` (`django_shop/shop/models.py`), выводятся в навбаре через context processor `get_categories_from_shop` (`django_shop/shop/context_processors.py`) и `base.html`.
- **Фильтрация**: только категория по URL (`/category/<id>/`) и поиск `?q=` (`django_shop/shop/views.py`).
- **Промокодов нет**: логика цен в `django_shop/cart/cart_services.py` и `django_shop/orders/models.py`.
- **Карточка товара**: кликабельна только картинка в `django_shop/shop/templates/shop/product/list.html`.

## Цели модернизации

1) Подготовить БД и доступ (суперюзер) перед изменениями моделей/фильтров.
2) Перевести внешний вид на Tailwind + сборка через Vite, **без SPA**.
3) Перенести «Категории» в блок фильтров и добавить новые фильтры.
4) Реализовать промокоды: модель + админка + endpoint(ы) + применение в корзине и повторная валидация при создании заказа.
5) Сделать всю карточку товара кликабельной.

## Предлагаемая архитектура изменений

### A) БД/суперюзер

- **Базовый подход (рекомендуется)**: не пересоздавать БД без необходимости — добавить/изменить модели и выполнить миграции.
- **Когда пересоздавать SQLite оправдано**: если проект ещё без прод-данных и вы хотите «чистую» схему (быстрее), особенно перед добавлением новых сущностей (фильтры/промокоды).
- В любом случае в план включить шаги:
- создать суперюзера через `createsuperuser` (учитывая `users.CustomUser`, email как логин)
- бэкап/копию `db.sqlite3` перед миграциями

### B) Tailwind + Vite в Django templates

- Создать фронтенд-сборку на Node (Vite + Tailwind) и **выгружать билд в Django static**.
- Ключевые интеграции:
- `django_shop/shop/templates/shop/base.html`: подключение скомпилированного CSS (и при необходимости JS) из `static/`.
- `django_shop/django_shop/settings.py`: убедиться, что `STATICFILES_DIRS`/`STATIC_ROOT` корректны для dev/prod.
- Стратегия внедрения:
- Сначала подключить Tailwind рядом с текущими стилями (чтобы не «сломать» всё сразу).
- Затем постепенно переписать ключевые шаблоны: `base.html`, `product/list.html`, `product/detail.html`, корзина/оформление заказа.

### C) Фильтры и перенос категорий

- Перестать выводить категории только в навбаре и перенести в **боковой/верхний блок фильтров** на странице списка товаров.
- Реализовать единый «filter state» через query params (GET):
- `category` (или `category_id`), `q` (поиск), `price_min`, `price_max`, `sort`, дополнительные фильтры.
- Точки изменения:
- `django_shop/shop/views.py`: расширить `ShopHome.get_queryset()` и/или создать отдельный класс/миксин для фильтрации; привести `ShopCategory` к тому же механизму (чтобы категория тоже была фильтром, а не отдельной страницей).
- `django_shop/shop/templates/shop/product/list.html`: добавить блок фильтров (категории + новые фильтры), формы GET, сохранение выбранных значений.
- `django_shop/shop/context_processors.py` / `base.html`: убрать/упростить вывод категорий в навбаре (или оставить ссылку на страницу с фильтрами).
- **Новые фильтры (разумный дефолт)**:
- цена (min/max)
- сортировка (по цене/по новизне)
- наличие (в наличии/все)
- (опционально) автор, если это важно для вашего каталога

### D) Промокоды (модель + админка + endpoints)

- Создать новое приложение `promocodes`.
- Модель `PromoCode` (минимально необходимое):
- `code` (уникальный, uppercased)
- `discount_type` (percent/fixed)
- `discount_value` (Decimal)
- `valid_from`, `valid_to`, `is_active`
- (опционально) `usage_limit`, `used_count`
- Интеграция в корзину (сессия) и заказ:
- `django_shop/cart/cart_services.py`: хранить применённый код в сессии и считать скидку в `get_cart_total_price()`.
- `django_shop/orders/models.py`: добавить поле на заказ (например, FK/Code snapshot) и пересчитывать `total_cost` с учётом промокода.
- `django_shop/orders/views.py`: при создании заказа повторно валидировать промокод и фиксировать результат.
- Endpoints (без DRF, в стиле текущего проекта):
- `POST /cart/promocode/apply/` (валидирует и сохраняет в сессии)
- `POST /cart/promocode/remove/` (очистка)
- (опционально) `GET /cart/promocode/status/` для отображения применённого промокода в UI
- Админка:
- `django_shop/promocodes/admin.py`: CRUD промокодов (по аналогии со стилем `orders/admin.py`/`shop/admin.py`).

### E) Кликабельная карточка

- Изменить разметку карточки в `django_shop/shop/templates/shop/product/list.html`, чтобы ссылка оборачивала всю карточку, а не только `<img>`.
- Добавить стили для ссылки (сброс цвета/подчёркивания) в текущие стили или уже в tailwind-утилиты после подключения.

## Порядок работ (рекомендуемый)

1) **Подготовка БД**: бэкап, решение «миграции vs пересоздание», создание суперюзера.
2) **Vite + Tailwind**: добавить сборку, подключить итоговый CSS в `base.html`, проверить dev/prod.
3) **Каркас UI**: обновить `base.html` (header/nav/footer), затем `product/list.html`.
4) **Фильтры**: реализовать query-param фильтрацию и новый блок фильтров, перенести категории туда.
5) **Промокоды**: создать app+модель+миграции, админку, endpoints, интеграцию в корзину и создание заказа.
6) **Кликабельность карточек**: финальная правка разметки и hover/outline состояния.
7) **Регресс-проверка**: каталог, поиск, фильтры, корзина, оформление заказа, админка.

## Ключевые файлы, которые будут затронуты

- Фронт/шаблоны: 
- [C:/Main/Repo/DarlyDjango/django_shop/shop/templates/shop/base.html](C:/Main/Repo/DarlyDjango/django_shop/shop/templates/shop/base.html)
- [C:/Main/Repo/DarlyDjango/django_shop/shop/templates/shop/product/list.html](C:/Main/Repo/DarlyDjango/django_shop/shop/templates/shop/product/list.html)
- [C:/Main/Repo/DarlyDjango/django_shop/shop/templates/shop/product/detail.html](C:/Main/Repo/DarlyDjango/django_shop/shop/templates/shop/product/detail.html)
- Фильтрация/логика: 
- [C:/Main/Repo/DarlyDjango/django_shop/shop/views.py](C:/Main/Repo/DarlyDjango/django_shop/shop/views.py)
- [C:/Main/Repo/DarlyDjango/django_shop/shop/context_processors.py](C:/Main/Repo/DarlyDjango/django_shop/shop/context_processors.py)
- Промокоды/цены:
- [C:/Main/Repo/DarlyDjango/django_shop/cart/cart_services.py](C:/Main/Repo/DarlyDjango/django_shop/cart/cart_services.py)
- [C:/Main/Repo/DarlyDjango/django_shop/orders/models.py](C:/Main/Repo/DarlyDjango/django_shop/orders/models.py)
- [C:/Main/Repo/DarlyDjango/django_shop/orders/views.py](C:/Main/Repo/DarlyDjango/django_shop/orders/views.py)
- Стили (переходный период):
- [C:/Main/Repo/DarlyDjango/django_shop/django_shop/static/shop/css/base.css](C:/Main/Repo/DarlyDjango/django_shop/django_shop/static/shop/css/base.css)

## Риски и меры

- **Пересоздание БД**: быстрее, но потеря данных; миграции безопаснее.
- **Tailwind внедрение**: лучше поэтапно, чтобы не ломать текущий UI.
- **Промокоды**: обязательна повторная серверная валидация при создании заказа (не доверять данным из сессии/клиента).
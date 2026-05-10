# Django E-Commerce Platform

Plateforme e-commerce complète développée avec Django 6, PostgreSQL et JavaScript vanilla. Architecture modulaire avec back-office multi-rôles, chat support temps réel, panier AJAX, et génération de factures PDF.

---

## Table des matières

1. [Aperçu du projet](#aperçu-du-projet)
2. [Stack technique](#stack-technique)
3. [Architecture](#architecture)
4. [Fonctionnalités](#fonctionnalités)
5. [Modèles de données](#modèles-de-données)
6. [Rôles et permissions](#rôles-et-permissions)
7. [Installation](#installation)
8. [Configuration](#configuration)
9. [Lancement](#lancement)
10. [Structure des dossiers](#structure-des-dossiers)
11. [Diagrammes UML](#diagrammes-uml)

---

## Aperçu du projet

Ce projet est une plateforme e-commerce B2C complète avec :

- **Côté client** : catalogue, panier AJAX, wishlist, checkout, paiement simulé, suivi commandes, avis vérifiés, chat support
- **Côté admin** : back-office complet avec tableau de bord analytique, gestion des produits/commandes/utilisateurs, facturation PDF, modération avis, support client
- **Sécurité** : contrôle d'accès basé sur les rôles (RBAC) à 4 niveaux
- **UI** : bilingue français/anglais, cart drawer AJAX, recherche instantanée, interface responsive

---

## Stack technique

| Composant | Technologie |
|---|---|
| Framework backend | Django 6.0.4 |
| Base de données | PostgreSQL |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| PDF | ReportLab |
| Images | Pillow |
| Configuration | python-decouple |
| Driver PostgreSQL | psycopg2 |

---

## Architecture

Le projet suit une architecture **monolithique modulaire Django (MTV)** découpée en 10 applications :

```
ecommerce/
├── config/          → Configuration globale (settings, urls, wsgi, asgi)
├── accounts/        → Authentification, profil, portail client
├── catalog/         → Catalogue produits et catégories
├── cart/            → Panier AJAX avec coupons
├── orders/          → Commandes, checkout, paiement
├── reviews/         → Avis produits vérifiés
├── wishlist/        → Produits favoris
├── coupons/         → Codes de réduction
├── shipping/        → Zones et frais de livraison
├── core/            → Home, recherche, support chat, pages statiques
└── admin_panel/     → Back-office complet avec RBAC
```

### Context processors globaux

Chaque requête injecte automatiquement dans tous les templates :

| Processor | Données injectées |
|---|---|
| `cart.context_processors.cart_snapshot` | Contenu du panier pour le header |
| `core.context_processors.site_language` | Langue active (fr/en) |
| `core.context_processors.search_snapshot` | Suggestions et termes trending |
| `core.context_processors.header_mega_menu` | Menu navigation avec catégories |

---

## Fonctionnalités

### Côté client

| Fonctionnalité | Description |
|---|---|
| Inscription / Connexion | Formulaire Django standard avec redirection role-based |
| Profil utilisateur | Édition nom, email, mot de passe |
| Portail client | Dashboard : commandes, avis, wishlist, total dépensé, adresses |
| Catalogue produits | Filtrage par catégorie, couleur, fourchette de prix, tri, pagination |
| Recherche instantanée | Autocomplete AJAX (8 résultats, recherche fr + en) |
| Fiche produit | Galerie 4 miniatures, notes moyennes, avis, produits similaires |
| Panier AJAX | Drawer latéral, ajout/suppression/quantité sans rechargement |
| Wishlist | Toggle add/remove, page liste des favoris |
| Coupons | Application code promo (PERCENT ou FIXED), validation dates et usage |
| Checkout | Sélection zone de livraison, calcul frais, récap commande |
| Paiement COD | Paiement à la livraison → confirmation directe |
| Paiement simulé | Simulation carte bancaire → marquage `is_paid` |
| Suivi commandes | Historique complet, détail par commande, statuts |
| Annulation commande | Annulation (PENDING/PAID uniquement) avec restauration stock automatique |
| Avis vérifiés | Détection automatique achat vérifié via historique commandes |
| Support chat | Widget flottant, polling toutes les 5 secondes |
| Coupons disponibles | Liste des codes actifs et valides dans le portail |
| Multilingue fr/en | Bascule de langue persistée en session |
| Pages légales (×10) | CGV, politique retour, confidentialité, garantie, etc. |

### Côté admin (back-office)

| Fonctionnalité | Groupes autorisés |
|---|---|
| Dashboard KPIs (ventes, commandes, users) | SUPER_ADMIN, MANAGER |
| Graphique ventes 7 derniers jours | SUPER_ADMIN, MANAGER |
| Graphique répartition statuts commandes | SUPER_ADMIN, MANAGER |
| Alerte produits en stock faible | SUPER_ADMIN, MANAGER |
| CRUD Produits (images, galerie, couleurs, features) | SUPER_ADMIN, MANAGER |
| CRUD Catégories (fr/en, slug auto) | SUPER_ADMIN, MANAGER |
| CRUD Coupons (type, dates, limites) | SUPER_ADMIN, MANAGER |
| CRUD Zones de livraison (frais, seuil gratuit) | SUPER_ADMIN, MANAGER |
| Gestion commandes (liste, détail, statut) | Tous les groupes |
| Génération facture PDF | Tout le staff |
| Gestion utilisateurs (créer, modifier, désactiver) | SUPER_ADMIN uniquement |
| Modération avis (approuver, supprimer) | SUPER_ADMIN, SUPPORT |
| Interface support chat (répondre, fermer) | SUPER_ADMIN, SUPPORT |

---

## Modèles de données

### Schéma relationnel

```
User
 ├── [1:1] Cart ──[1:N]── CartItem ──[N:1]── Product
 │            └──[N:1]── Coupon
 ├── [1:N] Order ──[1:N]── OrderItem ──[N:1]── Product
 ├── [1:N] Review ──[N:1]── Product
 ├── [1:N] WishlistItem ──[N:1]── Product
 └── [1:1] SupportConversation ──[1:N]── SupportMessage

Product ──[N:1]── Category
ShippingZone (standalone, liée via Order.shipping_city)
```

### Entités principales

#### Product
```
name_fr, name_en, slug, description_fr, description_en
price, old_price, stock, low_stock_threshold
image, gallery_image_1..4, feature_1..4, colors
is_active, is_featured, category (FK)
```
Méthodes : `is_in_stock()`, `is_low_stock()`, `average_rating()`, `get_gallery_images()`, `get_color_list()`

#### Order
```
status : PENDING | PAID | SHIPPED | DELIVERED | CANCELLED
payment_method : COD | CARD
is_paid, paid_at
first_name, last_name, email, phone
address, city, postal_code, shipping_city, shipping_fee
total_amount
```

#### Coupon
```
code (unique), discount_type : PERCENT | FIXED
value, min_order_amount
start_date, end_date, usage_limit, used_count
is_active
```
Méthode : `is_valid()` → vérifie is_active + dates + usage_limit

#### SupportConversation / SupportMessage
```
SupportConversation : user (1:1), is_closed, client_visible_from, last_message_at
SupportMessage : body, is_staff, is_read, delivered_at, read_at
```
Propriétés : `unread_for_client`, `unread_for_support`

#### ShippingZone
```
city (unique), fee, free_shipping_threshold, is_active
```

---

## Rôles et permissions

Le projet utilise un système RBAC à 4 groupes Django :

| Groupe | Produits | Catégories | Commandes | Coupons | Shipping | Utilisateurs | Avis | Support |
|---|---|---|---|---|---|---|---|---|
| **SUPER_ADMIN** | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ | ✅ |
| **MANAGER** | ✅ CRUD | ✅ CRUD | ✅ | ✅ CRUD | ✅ CRUD | ❌ | ❌ | ❌ |
| **PREPARATEUR** | ❌ | ❌ | ✅ lecture | ❌ | ❌ | ❌ | ❌ | ❌ |
| **SUPPORT** | ❌ | ❌ | ✅ lecture | ❌ | ❌ | ❌ | ✅ | ✅ |

Le décorateur `@group_required(*groupes)` gère les accès. Les superusers Django contournent tous les groupes.

Les admins (is_staff=True) ne peuvent pas ajouter de produits au panier.

---

## Installation

### Prérequis

- Python 3.10+
- PostgreSQL 14+
- pip

### Étapes

```bash
# 1. Cloner le projet
git clone <repo-url>
cd ecommerce

# 2. Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer la base de données PostgreSQL
# Dans psql :
CREATE DATABASE ecommerce_db;
CREATE USER ecommerce_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;

# 5. Configurer les variables d'environnement (voir section Configuration)

# 6. Appliquer les migrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Créer les groupes de rôles
python manage.py shell
```

```python
from django.contrib.auth.models import Group
for name in ["SUPER_ADMIN", "MANAGER", "PREPARATEUR", "SUPPORT"]:
    Group.objects.get_or_create(name=name)
```

```bash
# 9. Collecter les fichiers statiques
python manage.py collectstatic

# 10. Lancer le serveur
python manage.py runserver
```

---

## Configuration

Créer un fichier `.env` à la racine du projet :

```env
# Base de données
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=votre_secret_key_django_ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI (optionnel, non utilisé en production actuellement)
OPENAI_API_KEY=
OPENAI_SUPPORT_MODEL=gpt-4o
```

---

## Lancement

```bash
# Développement
python manage.py runserver

# Accès client
http://127.0.0.1:8000/

# Accès back-office
http://127.0.0.1:8000/admin-panel/

# Accès Django Admin natif
http://127.0.0.1:8000/admin/
```

---

## Structure des dossiers

```
ecommerce/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/
│   ├── models.py         → Utilise le User Django standard
│   ├── views.py          → register, login, logout, profile, activity, coupons, addresses, reviews
│   ├── urls.py
│   ├── forms.py          → ProfileUpdateForm
│   └── templates/accounts/
│
├── catalog/
│   ├── models.py         → Category, Product
│   ├── views.py          → product_list (filtres/tri), product_detail
│   ├── urls.py
│   └── templates/catalog/
│
├── cart/
│   ├── models.py         → Cart (1:1 User), CartItem
│   ├── views.py          → add, remove, update, apply_coupon, remove_coupon, toggle
│   ├── urls.py
│   ├── context_processors.py   → cart_snapshot
│   └── templates/cart/
│
├── orders/
│   ├── models.py         → Order, OrderItem
│   ├── views.py          → checkout, order_success, order_history, order_detail, cancel_order, payment_page
│   ├── urls.py
│   └── templates/orders/
│
├── reviews/
│   ├── models.py         → Review (unique_together product+user, is_verified_purchase)
│   ├── views.py          → add_review
│   └── urls.py
│
├── wishlist/
│   ├── models.py         → WishlistItem (unique_together user+product)
│   ├── views.py          → wishlist_detail, add, remove, toggle
│   └── urls.py
│
├── coupons/
│   ├── models.py         → Coupon (PERCENT/FIXED, dates, usage_limit)
│   └── urls.py
│
├── shipping/
│   ├── models.py         → ShippingZone (city unique, fee, free_shipping_threshold)
│   └── urls.py
│
├── core/
│   ├── models.py         → SupportConversation, SupportMessage
│   ├── views.py          → home, search_page, search_suggestions, support_chat_*, set_language, footer_page
│   ├── urls.py
│   ├── context_processors.py   → site_language, search_snapshot, header_mega_menu
│   └── templates/core/
│
├── admin_panel/
│   ├── views.py          → dashboard, produits, catégories, commandes, coupons, shipping, users, avis, support
│   ├── urls.py
│   ├── decorators.py     → @staff_required, @group_required
│   ├── forms.py          → ProductForm, CategoryForm, CouponForm, ShippingZoneForm, AdminUserCreateForm, ...
│   └── templates/admin_panel/
│
├── static/
│   ├── js/
│   │   ├── base.js                   → Cart drawer, search, support chat, mobile nav (1000+ lignes)
│   │   ├── catalog/detail.js         → Galerie, quantité, add to cart AJAX
│   │   ├── cart/cart.js              → Carousel suggestions
│   │   ├── admin/shared/entity.js    → Table filtrée + pagination
│   │   ├── admin/dashboard.js        → Graphiques ChartJS
│   │   └── admin/{product,coupon,shipping,category,order,user,review}/
│   └── css/
│
├── templates/
│   ├── base.html
│   ├── core/
│   ├── accounts/         → Client portal + admin profile
│   ├── catalog/
│   ├── cart/
│   ├── orders/
│   ├── wishlist/
│   └── admin_panel/
│
├── media/                → Uploads (images produits)
├── manage.py
├── requirements.txt
└── .env
```

---

## Workflows métier

### Checkout complet

```
Panier non vide
    → [optionnel] Appliquer coupon (validation code, date, min_amount, usage)
    → Sélectionner ville de livraison
    → Calcul frais (gratuit si total >= seuil)
    → Revalidation stock de chaque article
    → Création Order + OrderItems (price snapshot)
    → Décrémentation stock
    → Incrémentation coupon.used_count
    → Vidage du panier
    → Si COD → page succès
    → Si CARD → page paiement simulé → is_paid=True → page succès
```

### Avis vérifié

```
Client soumet avis sur produit
    → Vérification : user a une commande (PAID/SHIPPED/DELIVERED) contenant ce produit ?
    → Oui : is_verified_purchase = True
    → Non : is_verified_purchase = False
    → Avis créé (ou mis à jour si existant)
    → is_approved = True par défaut, modifiable par SUPER_ADMIN/SUPPORT
```

### Support chat

```
Client ouvre le widget
    → SupportConversation créée si inexistante (OneToOne)
    → Polling toutes les 5s → GET /support/chat/status/ → unread_count
    → Client envoie message → POST /support/chat/send/ → SupportMessage(is_staff=False)
    → Admin voit la conversation dans /admin-panel/support/
    → Admin répond → SupportMessage(is_staff=True)
    → Client reçoit au prochain polling → messages marqués delivered puis read
```

### Annulation commande

```
Client clique "Annuler" sur commande
    → Vérification statut : PENDING ou PAID uniquement
    → Pour chaque OrderItem : product.stock += quantity
    → Order.status = CANCELLED
    → Redirection historique avec message confirmation
```

---

## Diagrammes UML

Les fichiers `.mmd` (Mermaid) sont disponibles à la racine du projet. Ouvrez-les sur [mermaid.live](https://mermaid.live) ou avec l'extension Mermaid dans VS Code.

| Fichier | Contenu |
|---|---|
| `01_use_case.mmd` | Diagramme de cas d'utilisation complet |
| `02_class_diagram.mmd` | Diagramme de classes complet |
| `03_sequence_order.mmd` | Séquence passage de commande |
| `04_sequence_support.mmd` | Séquence chat support |
| `05_activity_order.mmd` | Diagramme d'activité commande |
| `06_sequence_admin_product.mmd` | Séquence gestion produit admin |

---

## Variables d'environnement

| Variable | Obligatoire | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Clé secrète Django |
| `DEBUG` | ✅ | True en développement, False en production |
| `DB_NAME` | ✅ | Nom de la base PostgreSQL |
| `DB_USER` | ✅ | Utilisateur PostgreSQL |
| `DB_PASSWORD` | ✅ | Mot de passe PostgreSQL |
| `DB_HOST` | ✅ | Hôte PostgreSQL (localhost) |
| `DB_PORT` | ✅ | Port PostgreSQL (5432) |
| `OPENAI_API_KEY` | ❌ | Optionnel (fonctionnalité future) |
| `OPENAI_SUPPORT_MODEL` | ❌ | Optionnel (fonctionnalité future) |

---

## Points importants

- Les admins (`is_staff=True`) ne peuvent pas ajouter de produits au panier — comportement intentionnel
- La revalidation du stock s'effectue deux fois : à l'ajout panier ET au checkout
- Les coupons sont en majuscules automatiquement (`.upper()`) — saisie insensible à la casse
- Le champ `Order.shipping_city` est un CharField lié par nom à `ShippingZone.city`
- La langue (fr/en) est persistée en session via `POST /set-language/`
- Le chat support fonctionne par polling HTTP (pas WebSocket) — mise à jour toutes les 5 secondes
- `DEBUG=True` doit être `False` en production avec `ALLOWED_HOSTS` configuré

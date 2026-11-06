import os
import random
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from catalog.models import Category, Product
from cart.models import Cart, CartItem
from coupons.models import Coupon
from orders.models import Order, OrderItem
from reviews.models import Review
from shipping.models import ShippingZone
from wishlist.models import WishlistItem
from core.models import SupportConversation, SupportMessage

User = get_user_model()


def generate_placeholder_image(output_path: Path, title: str, category_name: str, bg_color: tuple, text_color: tuple = (255, 255, 255)):
    """Generate a clean product placeholder image using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (600, 600), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Draw subtle inner frame
        draw.rectangle([(20, 20), (580, 580)], outline=(255, 255, 255, 40), width=2)

        # Draw category pill
        pill_text = f"  {category_name.upper()}  "
        draw.rectangle([(50, 50), (220, 85)], fill=(0, 0, 0, 100), outline=None)
        draw.text((60, 58), pill_text, fill=(255, 255, 255))

        # Draw Title
        words = title.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 22:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        y = 240
        for line in lines[:3]:
            draw.text((50, y), line, fill=text_color)
            y += 36

        # Draw brand footer
        draw.line([(50, 520), (550, 520)], fill=(255, 255, 255), width=1)
        draw.text((50, 535), "M&Y SHOP - ORIGINAL QUALITY", fill=(240, 240, 240))

        img.save(str(output_path), format="PNG", quality=90)
        return True
    except Exception as exc:
        print(f"Warning: could not generate image for {title}: {exc}")
        return False


class Command(BaseCommand):
    help = "Populate database with complete production-ready sample data: categories, products, clients, orders, reviews, etc."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing data and reseed from scratch.",
        )
        parser.add_argument(
            "--auto",
            action="store_true",
            help="Seed only if database is currently empty (recommended for deploy scripts).",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        auto = options.get("auto", False)

        if auto and Product.objects.exists() and User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("[seed_db] Database already seeded. Skipping (--auto)."))
            return

        if force:
            self.stdout.write(self.style.WARNING("[seed_db] Cleaning existing data (--force)..."))
            with transaction.atomic():
                OrderItem.objects.all().delete()
                Order.objects.all().delete()
                CartItem.objects.all().delete()
                Cart.objects.all().delete()
                WishlistItem.objects.all().delete()
                Review.objects.all().delete()
                SupportMessage.objects.all().delete()
                SupportConversation.objects.all().delete()
                Product.objects.all().delete()
                Category.objects.all().delete()
                Coupon.objects.all().delete()
                ShippingZone.objects.all().delete()
                User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.MIGRATE_HEADING("=== Starting E-Commerce Database Seeding ==="))

        with transaction.atomic():
            self._create_groups()
            users = self._create_users()
            self._create_shipping_zones()
            coupons = self._create_coupons()
            categories = self._create_categories()
            products = self._create_products(categories)
            self._create_reviews(products, users)
            self._create_orders(products, users)
            self._create_carts_and_wishlists(products, users, coupons)
            self._create_support(users)

        self.stdout.write(self.style.SUCCESS("\n[seed_db] COMPLETE! The database has been populated with rich data."))
        self.stdout.write(self.style.SUCCESS("Admin Credentials:"))
        self.stdout.write("  - Admin URL:       /admin-panel/ ou /admin/")
        self.stdout.write("  - Super Admin:     admin / Admin123!")
        self.stdout.write("  - Manager:         manager / Manager123!")
        self.stdout.write("  - Support Agent:   support / Support123!")
        self.stdout.write("  - Clients Démo:    youssef.alami (pass: Client123!), fatima.zahra, mehdi.bennani")

    def _create_groups(self):
        self.stdout.write("-> Creating security groups...")
        for name in ["SUPER_ADMIN", "MANAGER", "PREPARATEUR", "SUPPORT"]:
            Group.objects.get_or_create(name=name)

    def _create_users(self):
        self.stdout.write("-> Creating administrative and client users...")
        super_admin_group = Group.objects.get(name="SUPER_ADMIN")
        manager_group = Group.objects.get(name="MANAGER")
        prepa_group = Group.objects.get(name="PREPARATEUR")
        support_group = Group.objects.get(name="SUPPORT")

        # Superuser
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@myshop.ma",
                "first_name": "Admin",
                "last_name": "Principal",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.set_password("Admin123!")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        admin_user.groups.add(super_admin_group)

        # Staff Manager
        manager_user, _ = User.objects.get_or_create(
            username="manager",
            defaults={
                "email": "manager@myshop.ma",
                "first_name": "Yassine",
                "last_name": "El Fassi",
                "is_staff": True,
                "is_superuser": False,
            },
        )
        manager_user.set_password("Manager123!")
        manager_user.is_staff = True
        manager_user.save()
        manager_user.groups.add(manager_group)

        # Staff Preparateur
        prepa_user, _ = User.objects.get_or_create(
            username="preparateur",
            defaults={
                "email": "preparateur@myshop.ma",
                "first_name": "Amine",
                "last_name": "Naciri",
                "is_staff": True,
                "is_superuser": False,
            },
        )
        prepa_user.set_password("Prepa123!")
        prepa_user.is_staff = True
        prepa_user.save()
        prepa_user.groups.add(prepa_group)

        # Staff Support
        support_user, _ = User.objects.get_or_create(
            username="support",
            defaults={
                "email": "support@myshop.ma",
                "first_name": "Nour",
                "last_name": "Benjelloun",
                "is_staff": True,
                "is_superuser": False,
            },
        )
        support_user.set_password("Support123!")
        support_user.is_staff = True
        support_user.save()
        support_user.groups.add(support_group)

        # Clients
        client_data = [
            ("youssef.alami", "Youssef", "Alami", "youssef.alami@gmail.com", "0612345678", "Casablanca"),
            ("fatima.zahra", "Fatima-Zahra", "Mansouri", "fatima.zahra@gmail.com", "0623456789", "Rabat"),
            ("mehdi.bennani", "Mehdi", "Bennani", "mehdi.bennani@gmail.com", "0634567890", "Marrakech"),
            ("sarah.idrissi", "Sarah", "Idrissi", "sarah.idrissi@gmail.com", "0645678901", "Tanger"),
            ("omar.tazi", "Omar", "Tazi", "omar.tazi@gmail.com", "0656789012", "Fès"),
            ("amina.kabbaj", "Amina", "Kabbaj", "amina.kabbaj@gmail.com", "0667890123", "Agadir"),
            ("karim.chraibi", "Karim", "Chraibi", "karim.chraibi@gmail.com", "0678901234", "Casablanca"),
        ]

        clients = []
        for username, fname, lname, email, phone, city in client_data:
            client, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": fname,
                    "last_name": lname,
                    "email": email,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            client.set_password("Client123!")
            client.save()
            client._demo_city = city
            client._demo_phone = phone
            clients.append(client)

        return {
            "admin": admin_user,
            "manager": manager_user,
            "prepa": prepa_user,
            "support": support_user,
            "clients": clients,
        }

    def _create_shipping_zones(self):
        self.stdout.write("-> Creating Moroccan shipping zones...")
        zones = [
            ("Casablanca", Decimal("20.00"), Decimal("300.00")),
            ("Rabat", Decimal("25.00"), Decimal("350.00")),
            ("Marrakech", Decimal("35.00"), Decimal("400.00")),
            ("Tanger", Decimal("35.00"), Decimal("400.00")),
            ("Fès", Decimal("30.00"), Decimal("350.00")),
            ("Agadir", Decimal("40.00"), Decimal("500.00")),
            ("Oujda", Decimal("45.00"), Decimal("500.00")),
            ("Meknès", Decimal("30.00"), Decimal("350.00")),
            ("Kénitra", Decimal("25.00"), Decimal("350.00")),
            ("Mohammedia", Decimal("20.00"), Decimal("300.00")),
        ]
        for city, fee, threshold in zones:
            ShippingZone.objects.update_or_create(
                city=city,
                defaults={
                    "fee": fee,
                    "free_shipping_threshold": threshold,
                    "is_active": True,
                },
            )

    def _create_coupons(self):
        self.stdout.write("-> Creating promo coupons...")
        now = timezone.now()
        coupons_data = [
            ("BIENVENUE10", "PERCENT", Decimal("10.00"), Decimal("100.00"), 500),
            ("PROMO20", "PERCENT", Decimal("20.00"), Decimal("300.00"), 200),
            ("SOLDE50", "FIXED", Decimal("50.00"), Decimal("250.00"), 150),
            ("VIP100", "FIXED", Decimal("100.00"), Decimal("600.00"), 100),
            ("FLASH15", "PERCENT", Decimal("15.00"), Decimal("200.00"), 300),
            ("FREESHIP25", "FIXED", Decimal("25.00"), Decimal("150.00"), 500),
        ]
        coupons = []
        for code, discount_type, value, min_amount, limit in coupons_data:
            coupon, _ = Coupon.objects.update_or_create(
                code=code,
                defaults={
                    "discount_type": discount_type,
                    "value": value,
                    "min_order_amount": min_amount,
                    "start_date": now - timedelta(days=10),
                    "end_date": now + timedelta(days=90),
                    "usage_limit": limit,
                    "used_count": random.randint(3, 25),
                    "is_active": True,
                },
            )
            coupons.append(coupon)
        return coupons

    def _create_categories(self):
        self.stdout.write("-> Creating store categories...")
        # Note: names match header_mega_menu config
        categories_data = [
            ("Audio", "Audio", "audio"),
            ("Montre & Bureau", "Smart & Office", "montre-bureau"),
            ("Electromenager", "Home Appliances", "electromenager"),
            ("Soin personnel", "Personal Care", "soin-personnel"),
            ("Power", "Power & Energy", "power"),
            ("Smartphones & Accessoires", "Smartphones & Accessories", "smartphones-accessoires"),
            ("Gaming & Setup", "Gaming & Setup", "gaming-setup"),
        ]
        categories = {}
        for name_fr, name_en, slug in categories_data:
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name_fr": name_fr,
                    "name_en": name_en,
                    "is_active": True,
                },
            )
            categories[slug] = cat
        return categories

    def _create_products(self, categories):
        self.stdout.write("-> Creating catalog products with images...")
        media_products_dir = settings.MEDIA_ROOT / "products"
        media_products_dir.mkdir(parents=True, exist_ok=True)

        items = [
            # Audio
            {
                "category": categories["audio"],
                "name_fr": "Casque Bluetooth Sony WH-1000XM5 ANC",
                "name_en": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
                "slug": "sony-wh-1000xm5-anc",
                "price": Decimal("2890.00"),
                "old_price": Decimal("3490.00"),
                "stock": 18,
                "is_featured": True,
                "colors": "Noir, Argent Platine, Bleu Nuit",
                "features": ["Réduction active de bruit leader", "Autonomie jusqu'à 30h", "Audio Hi-Res sans fil", "Charge rapide USB-C"],
                "desc_fr": "Le casque Sony WH-1000XM5 réinvente l'écoute sans distraction grâce à son double processeur de réduction de bruit et ses 8 micros haute sensibilité. Un son d'une clarté exceptionnelle.",
                "desc_en": "Industry-leading noise canceling headphones with dual processors and 8 microphones. Enjoy Hi-Res wireless audio and up to 30 hours of battery life.",
                "bg_color": (30, 41, 59),
            },
            {
                "category": categories["audio"],
                "name_fr": "Écouteurs Sans Fil Apple AirPods Pro 2 USB-C",
                "name_en": "Apple AirPods Pro 2 Wireless Earbuds USB-C",
                "slug": "apple-airpods-pro-2-usb-c",
                "price": Decimal("2450.00"),
                "old_price": Decimal("2790.00"),
                "stock": 25,
                "is_featured": True,
                "colors": "Blanc",
                "features": ["Puce Apple H2 surpuissante", "Réduction active 2x plus efficace", "Boîtier MagSafe USB-C", "Audio spatial personnalisé"],
                "desc_fr": "Les AirPods Pro 2 intègrent la puce H2 pour une réduction de bruit deux fois plus efficace et un rendu audio spatial bluffant.",
                "desc_en": "AirPods Pro 2 feature up to 2x more Active Noise Cancellation, Adaptive Audio, and USB-C charging case.",
                "bg_color": (24, 24, 27),
            },
            {
                "category": categories["audio"],
                "name_fr": "Enceinte Portable JBL Charge 5 Étanche",
                "name_en": "JBL Charge 5 Waterproof Portable Speaker",
                "slug": "jbl-charge-5-etanche",
                "price": Decimal("1390.00"),
                "old_price": Decimal("1650.00"),
                "stock": 14,
                "is_featured": False,
                "colors": "Noir, Bleu Océan, Rouge, Camouflage",
                "features": ["Son JBL Pro puissant", "Autonomie de 20 heures", "Étanche IP67 poussière et eau", "Powerbank intégré"],
                "desc_fr": "Emportez la fête partout avec l'enceinte JBL Charge 5. Haut-parleur optimisé longue portée et double radiateur de basses passif.",
                "desc_en": "Take the party with you no matter what the weather with the bold JBL Charge 5 portable speaker.",
                "bg_color": (15, 23, 42),
            },
            {
                "category": categories["audio"],
                "name_fr": "Écouteurs Sport Anker Soundcore Life P3",
                "name_en": "Anker Soundcore Life P3 Noise Cancelling Earbuds",
                "slug": "anker-soundcore-life-p3",
                "price": Decimal("590.00"),
                "old_price": Decimal("750.00"),
                "stock": 30,
                "is_featured": False,
                "colors": "Noir, Blanc, Bleu Ciel",
                "features": ["Réduction de bruit multimode", "Basses BassUp surpuissantes", "6 micros avec IA", "Autonomie jusqu'à 35h"],
                "desc_fr": "Son dynamique haute définition avec technologie BassUp et trois modes de réduction de bruit ambiant.",
                "desc_en": "Life P3 noise cancelling earbuds feature custom 11mm composite drivers and 6 microphones with AI uplink noise reduction.",
                "bg_color": (30, 58, 138),
            },

            # Montre & Bureau
            {
                "category": categories["montre-bureau"],
                "name_fr": "Montre Connectée Apple Watch Series 9 GPS 45mm",
                "name_en": "Apple Watch Series 9 GPS 45mm Smartwatch",
                "slug": "apple-watch-series-9-45mm",
                "price": Decimal("4190.00"),
                "old_price": Decimal("4690.00"),
                "stock": 12,
                "is_featured": True,
                "colors": "Minuit, Lumière Stellaire, Argent",
                "features": ["Puce SiP S9 surpuissante", "Geste Toucher deux fois magique", "Écran éclatant 2000 nits", "Suivi santé avancé ECG"],
                "desc_fr": "Plus puissante, plus lumineuse, l'Apple Watch Series 9 révolutionne vos interactions au quotidien avec le geste double-tap.",
                "desc_en": "A magically new way to use your Apple Watch without touching the screen, powered by the S9 SiP chip.",
                "bg_color": (2, 6, 23),
            },
            {
                "category": categories["montre-bureau"],
                "name_fr": "Montre Connectée Samsung Galaxy Watch 6 44mm",
                "name_en": "Samsung Galaxy Watch 6 44mm Bluetooth",
                "slug": "samsung-galaxy-watch-6-44mm",
                "price": Decimal("2290.00"),
                "old_price": Decimal("2690.00"),
                "stock": 9,
                "is_featured": False,
                "colors": "Graphite, Argent",
                "features": ["Écran Sapphire Crystal 20% plus grand", "Suivi avancé du sommeil", "Capteur BioActive 3-en-1", "Charge sans fil rapide"],
                "desc_fr": "Prenez soin de votre bien-être jour et nuit avec la Galaxy Watch 6 et son grand écran haute définition.",
                "desc_en": "Start your everyday wellness journey with a larger display, customized workout routines, and sleep analysis.",
                "bg_color": (23, 37, 84),
            },
            {
                "category": categories["montre-bureau"],
                "name_fr": "Clavier Sans Fil Logitech MX Keys S Rétroéclairé",
                "name_en": "Logitech MX Keys S Wireless Illuminated Keyboard",
                "slug": "logitech-mx-keys-s",
                "price": Decimal("1090.00"),
                "old_price": Decimal("1290.00"),
                "stock": 16,
                "is_featured": False,
                "colors": "Gris Graphite, Gris Pâle",
                "features": ["Frappe fluide Perfect Stroke", "Rétroéclairage intelligent", "Multi-dispositifs Easy-Switch", "Connexion Bluetooth & Logi Bolt"],
                "desc_fr": "Clavier sans fil haut de gamme conçu pour une frappe fluide, rapide et silencieuse avec touches profilées.",
                "desc_en": "Master your workflow with precise, fast fluid typing and smart illumination with proximity sensors.",
                "bg_color": (31, 41, 55),
            },
            {
                "category": categories["montre-bureau"],
                "name_fr": "Souris Ergonomique Logitech MX Master 3S",
                "name_en": "Logitech MX Master 3S Performance Mouse",
                "slug": "logitech-mx-master-3s",
                "price": Decimal("890.00"),
                "old_price": Decimal("1090.00"),
                "stock": 22,
                "is_featured": True,
                "colors": "Graphite, Gris Pâle",
                "features": ["Capteur optique 8000 DPI sur verre", "Clics silencieux Quiet Clicks", "Molette MagSpeed électromagnétique", "Autonomie 70 jours"],
                "desc_fr": "L'icône remasterisée pour les créateurs et développeurs avec clics silencieux et défilement ultra-rapide.",
                "desc_en": "An icon remastered with Quiet Clicks and 8,000 DPI track-on-glass sensor for ultimate precision.",
                "bg_color": (17, 24, 39),
            },

            # Power
            {
                "category": categories["power"],
                "name_fr": "Batterie Externe Anker 737 Power Bank 24000mAh 140W",
                "name_en": "Anker 737 Power Bank (PowerCore 24K) 140W",
                "slug": "anker-737-power-bank-140w",
                "price": Decimal("1150.00"),
                "old_price": Decimal("1390.00"),
                "stock": 15,
                "is_featured": True,
                "colors": "Noir Titane",
                "features": ["Charge ultra-rapide bidirectionnelle 140W", "Écran digital intelligent couleur", "Capacité colossale 24000 mAh", "Compatible MacBook Pro"],
                "desc_fr": "Rechargez un MacBook Pro 16 pouces à 50% en seulement 40 minutes grâce à la puissance record de 140W.",
                "desc_en": "Equipped with the latest Power Delivery 3.1 and bi-directional technology to quickly recharge the portable charger or get a 140W ultra-powerful charge.",
                "bg_color": (9, 9, 11),
            },
            {
                "category": categories["power"],
                "name_fr": "Chargeur Rapide GaN Baseus 65W 3 Ports USB-C",
                "name_en": "Baseus GaN5 Pro 65W Fast Charger 3-Port",
                "slug": "baseus-gan-65w-3ports",
                "price": Decimal("299.00"),
                "old_price": Decimal("390.00"),
                "stock": 35,
                "is_featured": False,
                "colors": "Noir, Blanc",
                "features": ["Technologie GaN 5e génération", "2 ports USB-C + 1 USB-A", "Protection intelligente contre surchauffe", "Ultra compact et léger"],
                "desc_fr": "Un seul chargeur de poche pour votre PC portable, tablette et smartphone en même temps.",
                "desc_en": "Compact and powerful 65W wall charger featuring advanced GaN technology and multi-device support.",
                "bg_color": (30, 41, 59),
            },
            {
                "category": categories["power"],
                "name_fr": "Station de Charge MagSafe 3-en-1 Belkin BoostCharge",
                "name_en": "Belkin BoostCharge Pro 3-in-1 Wireless Charger",
                "slug": "belkin-magsafe-3en1",
                "price": Decimal("890.00"),
                "old_price": Decimal("1090.00"),
                "stock": 8,
                "is_featured": False,
                "colors": "Blanc, Noir",
                "features": ["Charge sans fil rapide 15W MagSafe", "Recharge iPhone, Apple Watch et AirPods", "Design architectural moderne", "Certifié officiel Apple"],
                "desc_fr": "Alimentez l'ensemble de votre écosystème Apple sur une seule station design et élégante.",
                "desc_en": "Charge your Apple devices faster with this beautifully designed charging stand featuring the new magnetic fast charging module.",
                "bg_color": (39, 39, 42),
            },

            # Electromenager
            {
                "category": categories["electromenager"],
                "name_fr": "Aspirateur Robot Laveur Roborock S8 Pro Ultra",
                "name_en": "Roborock S8 Pro Ultra Robot Vacuum and Mop",
                "slug": "roborock-s8-pro-ultra",
                "price": Decimal("4490.00"),
                "old_price": Decimal("5290.00"),
                "stock": 6,
                "is_featured": True,
                "colors": "Blanc, Noir",
                "features": ["Station tout-en-un vidage & séchage", "Aspiration surpuissante 6000 Pa", "Double brosse DuoRoller", "Navigation laser LiDAR précise"],
                "desc_fr": "Le summum du nettoyage autonome avec station autonettoyante intelligente et brosses anti-emmêlement.",
                "desc_en": "Forget about cleaning with the all-in-one docking station and DuoRoller Riser brush system.",
                "bg_color": (15, 23, 42),
            },
            {
                "category": categories["electromenager"],
                "name_fr": "Friteuse Sans Huile Airfryer Philips XXL 7.2L",
                "name_en": "Philips Premium Airfryer XXL 7.2L Connected",
                "slug": "philips-airfryer-xxl-7l",
                "price": Decimal("1890.00"),
                "old_price": Decimal("2290.00"),
                "stock": 14,
                "is_featured": True,
                "colors": "Noir & Cuivre",
                "features": ["Technologie Rapid Air 90% moins de gras", "Capacité familiale 1.4 kg / 7.2 L", "Application NutriU recettes guidées", "16 fonctions de cuisson en 1"],
                "desc_fr": "Cuisinez croustillant et sainement pour toute la famille avec un air chaud circulant à grande vitesse.",
                "desc_en": "Delicious fries with up to 90% less fat thanks to Rapid Air technology and smart sensing.",
                "bg_color": (31, 41, 55),
            },
            {
                "category": categories["electromenager"],
                "name_fr": "Purificateur d'Air Intelligent Xiaomi Smart Air Purifier 4",
                "name_en": "Xiaomi Smart Air Purifier 4 High Efficiency",
                "slug": "xiaomi-smart-air-purifier-4",
                "price": Decimal("1290.00"),
                "old_price": Decimal("1490.00"),
                "stock": 11,
                "is_featured": False,
                "colors": "Blanc Minimaliste",
                "features": ["Filtre 3-en-1 élimine 99.97% des particules", "Couvre une pièce jusqu'à 48m²", "Écran tactile OLED intuitif", "Contrôle vocal Google & Alexa"],
                "desc_fr": "Respirez un air pur et sain dans votre maison en temps réel avec capteurs laser haute précision.",
                "desc_en": "Breathe clean, healthy air. The 3-in-1 filtration system eliminates odors and fine particles.",
                "bg_color": (30, 41, 59),
            },
            {
                "category": categories["electromenager"],
                "name_fr": "Machine à Café Expresso Automatique De'Longhi Magnifica S",
                "name_en": "De'Longhi Magnifica S Bean to Cup Coffee Maker",
                "slug": "delonghi-magnifica-s",
                "price": Decimal("3990.00"),
                "old_price": Decimal("4690.00"),
                "stock": 7,
                "is_featured": False,
                "colors": "Noir & Argent",
                "features": ["Broyeur grains conique intégré acier", "Buse vapeur manuelle cappuccino", "Personnalisation arôme et mouture", "Nettoyage automatique facile"],
                "desc_fr": "Du grain fraîchement moulu à la tasse d'un seul geste pour un expresso digne des plus grands cafés italiens.",
                "desc_en": "Enjoy delicious barista-quality espresso and creamy cappuccinos at the touch of a button.",
                "bg_color": (24, 24, 27),
            },

            # Soin personnel
            {
                "category": categories["soin-personnel"],
                "name_fr": "Tondeuse Multifonction Philips Series 7000 14-en-1",
                "name_en": "Philips Norelco Multigroom Series 7000 14-in-1",
                "slug": "philips-multigroom-7000",
                "price": Decimal("490.00"),
                "old_price": Decimal("620.00"),
                "stock": 28,
                "is_featured": False,
                "colors": "Acier Brossé",
                "features": ["14 outils pour barbe, cheveux et corps", "Lames DualCut auto-affûtées", "Autonomie 5 heures sans fil", "100% étanche sous la douche"],
                "desc_fr": "Polyvalence ultime et précision professionnelle pour tondre et sculpter barbe, cheveux et corps.",
                "desc_en": "Craft your personal look with this versatile trimmer featuring tempered steel blades that will not break.",
                "bg_color": (15, 23, 42),
            },
            {
                "category": categories["soin-personnel"],
                "name_fr": "Brosse à Dents Électrique Oral-B iO Series 9 Connectée",
                "name_en": "Oral-B iO Series 9 Electric Toothbrush AI Tracking",
                "slug": "oral-b-io-series-9",
                "price": Decimal("1790.00"),
                "old_price": Decimal("2190.00"),
                "stock": 13,
                "is_featured": False,
                "colors": "Noir Onyx, Blanc Quartz",
                "features": ["Technologie magnétique révolutionnaire iO", "Suivi 3D des dents avec IA", "7 modes de brossage intelligents", "Étui de voyage chargeur inclus"],
                "desc_fr": "Une sensation de propreté purifiante professionnelle et un brossage guidé en direct par intelligence artificielle.",
                "desc_en": "Combines powerful micro-vibrations with Oral-B's unique dentist-inspired round brush head.",
                "bg_color": (30, 58, 138),
            },

            # Gaming & Setup
            {
                "category": categories["gaming-setup"],
                "name_fr": "Manette Sans Fil Sony PlayStation DualSense Edge",
                "name_en": "Sony PlayStation DualSense Edge Wireless Controller",
                "slug": "dualsense-edge-ps5",
                "price": Decimal("1890.00"),
                "old_price": Decimal("2250.00"),
                "stock": 10,
                "is_featured": True,
                "colors": "Blanc & Noir",
                "features": ["Gâchettes adaptatives réglables", "Palettes arrière configurables", "Retour haptique immersif", "Modules de joystick remplaçables"],
                "desc_fr": "Obtenez un avantage compétitif avec la manette pro ultra-personnalisable pour PlayStation 5 et PC.",
                "desc_en": "Engineered for high performance and personalization with swappable stick caps and remappable back buttons.",
                "bg_color": (17, 24, 39),
            },
            {
                "category": categories["gaming-setup"],
                "name_fr": "Écran Gaming Incurvé Samsung Odyssey G5 27\" 144Hz 2K",
                "name_en": "Samsung Odyssey G5 27\" WQHD 144Hz Curved Gaming Monitor",
                "slug": "samsung-odyssey-g5-27",
                "price": Decimal("2590.00"),
                "old_price": Decimal("2990.00"),
                "stock": 8,
                "is_featured": True,
                "colors": "Noir Mat",
                "features": ["Résolution WQHD 2560 x 1440", "Courbure 1000R immersive", "Taux de rafraîchissement 144 Hz", "Temps de réponse 1 ms MPRT"],
                "desc_fr": "Plongez au cœur de l'action avec la courbure 1000R ultra-immersive et la fluidité extrême 144Hz.",
                "desc_en": "Curved gaming monitor designed to match the human eye contours for unbelievable realism.",
                "bg_color": (3, 7, 18),
            },

            # Smartphones
            {
                "category": categories["smartphones-accessoires"],
                "name_fr": "Support Voiture Magnétique Magsafe avec Charge Rapide 15W",
                "name_en": "Magnetic Wireless Car Mount Fast Charging 15W",
                "slug": "support-voiture-magsafe-15w",
                "price": Decimal("249.00"),
                "old_price": Decimal("320.00"),
                "stock": 40,
                "is_featured": False,
                "colors": "Noir, Argent",
                "features": ["Aimants N52 ultra puissants", "Rotation 360 degrés réglable", "Fixation solide sur grille d'aération", "Câble USB-C inclus"],
                "desc_fr": "Fixez et chargez votre smartphone instantanément d'une seule main sur la route.",
                "desc_en": "Strong magnetic hold with up to 15W wireless charging speed on all MagSafe compatible phones.",
                "bg_color": (31, 41, 55),
            },
        ]

        products = []
        for it in items:
            prod_slug = it["slug"]
            cat = it["category"]
            cat_name = cat.name_fr

            # Generate image file
            img_rel_path = f"products/{prod_slug}.png"
            img_abs_path = settings.MEDIA_ROOT / img_rel_path
            generate_placeholder_image(img_abs_path, it["name_fr"], cat_name, it["bg_color"])

            feats = it.get("features", [])
            f1 = feats[0] if len(feats) > 0 else ""
            f2 = feats[1] if len(feats) > 1 else ""
            f3 = feats[2] if len(feats) > 2 else ""
            f4 = feats[3] if len(feats) > 3 else ""

            prod, _ = Product.objects.update_or_create(
                slug=prod_slug,
                defaults={
                    "category": cat,
                    "name_fr": it["name_fr"],
                    "name_en": it["name_en"],
                    "description_fr": it["desc_fr"],
                    "description_en": it["desc_en"],
                    "price": it["price"],
                    "old_price": it.get("old_price"),
                    "stock": it["stock"],
                    "low_stock_threshold": 5,
                    "image": img_rel_path,
                    "feature_1": f1,
                    "feature_2": f2,
                    "feature_3": f3,
                    "feature_4": f4,
                    "colors": it.get("colors", ""),
                    "is_active": True,
                    "is_featured": it.get("is_featured", False),
                },
            )
            products.append(prod)

        return products

    def _create_reviews(self, products, users):
        self.stdout.write("-> Creating realistic customer reviews...")
        clients = users["clients"]
        reviews_data = [
            (5, "Produit exceptionnel ! La réduction de bruit est bluffante et la batterie tient largement mes journées de travail. Recommandé les yeux fermés."),
            (5, "Livraison très rapide à Casablanca en moins de 24h. Emballage soigné, produit 100% authentique. Bravo à l'équipe M&Y."),
            (4, "Très bonne qualité globale. Facile à configurer et design très élégant. Seul bémol le prix un peu élevé mais justifié."),
            (5, "Super rapport qualité prix, rien à redire ! Conforme à la description sur le site."),
            (4, "Fonctionne parfaitement. L'autonomie est au rendez-vous et la finition est premium."),
            (5, "Service client au top qui m'a bien conseillé sur WhatsApp avant ma commande. Très satisfait !"),
            (3, "Bon produit mais j'aurais aimé une couleur plus claire. Fait bien son travail."),
            (5, "Incroyable expérience d'achat. C'est déjà ma 3ème commande sur cette boutique et toujours le même sérieux."),
        ]

        created_count = 0
        for i, prod in enumerate(products[:12]):
            # Assign 2-3 reviews per product from distinct clients
            sample_clients = random.sample(clients, min(3, len(clients)))
            for j, client in enumerate(sample_clients):
                rating, comment = random.choice(reviews_data)
                Review.objects.update_or_create(
                    product=prod,
                    user=client,
                    defaults={
                        "rating": rating,
                        "comment": comment,
                        "is_verified_purchase": True,
                        "is_approved": True,
                    },
                )
                created_count += 1

    def _create_orders(self, products, users):
        self.stdout.write("-> Creating orders & transactions across the last 7 days...")
        clients = users["clients"]
        now = timezone.now()

        # Distribution of statuses for rich dashboard reporting
        order_templates = [
            # Day 0 (Today)
            {"offset_days": 0, "status": "PENDING", "payment": "COD", "paid": False, "client_idx": 0},
            {"offset_days": 0, "status": "PAID", "payment": "CARD", "paid": True, "client_idx": 1},
            {"offset_days": 0, "status": "DELIVERED", "payment": "CARD", "paid": True, "client_idx": 2},

            # Day 1
            {"offset_days": 1, "status": "SHIPPED", "payment": "COD", "paid": True, "client_idx": 3},
            {"offset_days": 1, "status": "PAID", "payment": "CARD", "paid": True, "client_idx": 4},

            # Day 2
            {"offset_days": 2, "status": "DELIVERED", "payment": "CARD", "paid": True, "client_idx": 5},
            {"offset_days": 2, "status": "DELIVERED", "payment": "COD", "paid": True, "client_idx": 6},

            # Day 3
            {"offset_days": 3, "status": "SHIPPED", "payment": "CARD", "paid": True, "client_idx": 0},
            {"offset_days": 3, "status": "CANCELLED", "payment": "COD", "paid": False, "client_idx": 1},

            # Day 4
            {"offset_days": 4, "status": "DELIVERED", "payment": "CARD", "paid": True, "client_idx": 2},
            {"offset_days": 4, "status": "PAID", "payment": "CARD", "paid": True, "client_idx": 3},

            # Day 5
            {"offset_days": 5, "status": "DELIVERED", "payment": "COD", "paid": True, "client_idx": 4},

            # Day 6
            {"offset_days": 6, "status": "DELIVERED", "payment": "CARD", "paid": True, "client_idx": 5},
            {"offset_days": 6, "status": "SHIPPED", "payment": "COD", "paid": True, "client_idx": 6},
        ]

        addresses_by_city = {
            "Casablanca": ("Boulevard d'Anfa, Résidence Al Manar", "20000", Decimal("20.00")),
            "Rabat": ("Avenue Mohammed VI, Souissi", "10000", Decimal("25.00")),
            "Marrakech": ("Boulevard Mohamed V, Guéliz", "40000", Decimal("35.00")),
            "Tanger": ("Avenue des Forces Armées Royales, Malabata", "90000", Decimal("35.00")),
            "Fès": ("Avenue Hassan II, Ville Nouvelle", "30000", Decimal("30.00")),
            "Agadir": ("Boulevard du 20 Août, Secteur Touristique", "80000", Decimal("40.00")),
        }

        for idx, ot in enumerate(order_templates):
            client = clients[ot["client_idx"] % len(clients)]
            city = getattr(client, "_demo_city", "Casablanca")
            address_info = addresses_by_city.get(city, ("Boulevard Mohammed V", "20000", Decimal("25.00")))
            address_line, postal, ship_fee = address_info

            # Select 1 to 3 items
            selected_products = random.sample(products, random.randint(1, 3))
            
            created_time = now - timedelta(days=ot["offset_days"], hours=random.randint(1, 10), minutes=random.randint(0, 59))
            paid_time = created_time + timedelta(minutes=15) if ot["paid"] else None

            order = Order.objects.create(
                user=client,
                payment_method=ot["payment"],
                is_paid=ot["paid"],
                paid_at=paid_time,
                first_name=client.first_name,
                last_name=client.last_name,
                email=client.email,
                phone=getattr(client, "_demo_phone", "0612345678"),
                shipping_city=city,
                shipping_fee=ship_fee,
                address=address_line,
                city=city,
                postal_code=postal,
                status=ot["status"],
                total_amount=Decimal("0.00"),
            )

            total = Decimal("0.00")
            for prod in selected_products:
                qty = random.randint(1, 2)
                item_price = prod.price
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    price=item_price,
                    quantity=qty,
                )
                total += item_price * qty

            # Add shipping fee if not eligible for free shipping
            if total < Decimal("500.00"):
                total += ship_fee

            order.total_amount = total
            order.save()

            # Update created_at timestamp in database (bypassing auto_now_add)
            Order.objects.filter(id=order.id).update(created_at=created_time)

    def _create_carts_and_wishlists(self, products, users, coupons):
        self.stdout.write("-> Creating active customer carts and wishlists...")
        clients = users["clients"]
        if not clients:
            return

        # Client 0 Cart with items and coupon applied
        client0 = clients[0]
        cart0, _ = Cart.objects.get_or_create(user=client0)
        cart0.items.all().delete()
        CartItem.objects.create(cart=cart0, product=products[0], quantity=1)
        CartItem.objects.create(cart=cart0, product=products[1], quantity=2)
        cart0.coupon = coupons[0]  # BIENVENUE10
        cart0.save()

        # Client 1 Cart
        client1 = clients[1]
        cart1, _ = Cart.objects.get_or_create(user=client1)
        cart1.items.all().delete()
        CartItem.objects.create(cart=cart1, product=products[4], quantity=1)
        cart1.save()

        # Wishlists
        for client in clients[:4]:
            favorite_prods = random.sample(products, 3)
            for prod in favorite_prods:
                WishlistItem.objects.get_or_create(user=client, product=prod)

    def _create_support(self, users):
        self.stdout.write("-> Creating support conversations & messages...")
        clients = users["clients"]
        support_agent = users["support"]

        client = clients[0]  # Youssef Alami
        conv, _ = SupportConversation.objects.get_or_create(
            user=client,
            defaults={"is_closed": False, "client_visible_from": timezone.now()},
        )
        conv.messages.all().delete()

        SupportMessage.objects.create(
            conversation=conv,
            sender=client,
            body="Bonjour, est-ce que le casque Sony WH-1000XM5 bénéficie d'une garantie constructeur officielle ?",
            is_staff=False,
            is_read=True,
        )
        SupportMessage.objects.create(
            conversation=conv,
            sender=support_agent,
            body="Bonjour Youssef, oui absolument ! Tous nos articles Sony disposent d'une garantie constructeur de 1 an avec facture officielle.",
            is_staff=True,
            is_read=True,
        )
        SupportMessage.objects.create(
            conversation=conv,
            sender=client,
            body="Parfait, merci beaucoup pour votre réactivité !",
            is_staff=False,
            is_read=True,
        )


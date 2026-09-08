"""
Commande de gestion pour générer des données de démonstration
(section 22 du cahier des charges) : entreprise, utilisateurs,
produits, fournisseurs de démo.

Usage : python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand

from accounts.models import User
from customers.models import Customer
from products.models import Category, Product
from settings_app.models import CompanySettings
from suppliers.models import Supplier


class Command(BaseCommand):
    help = "Génère des données de démonstration pour StockManager (Kamsar Street)."

    def handle(self, *args, **options):
        CompanySettings.get_solo()

        users_data = [
            ('severin', 'Sévérin', 'Camara', 'admin', True),
            ('mamadou', 'Mamadou', 'Diallo', 'manager', False),
            ('fatou', 'Fatou', 'Bah', 'seller', False),
        ]
        for username, first, last, role, is_super in users_data:
            if not User.objects.filter(username=username).exists():
                if is_super:
                    User.objects.create_superuser(username, f'{username}@kamsarstreet.gn', 'ChangeMoi123!', first_name=first, last_name=last, role=role)
                else:
                    User.objects.create_user(username, f'{username}@kamsarstreet.gn', 'ChangeMoi123!', first_name=first, last_name=last, role=role)
                self.stdout.write(self.style.SUCCESS(f"Utilisateur créé : {username} / ChangeMoi123!"))

        cat_informatique, _ = Category.objects.get_or_create(name='Informatique')
        cat_stockage, _ = Category.objects.get_or_create(name='Stockage')
        cat_reseau, _ = Category.objects.get_or_create(name='Réseau')

        sup_abc, _ = Supplier.objects.get_or_create(name='ABC Distribution', defaults={'email': 'contact@abcdist.gn', 'phone': '+224 622 12 34 56', 'address': 'Conakry'})
        sup_tech, _ = Supplier.objects.get_or_create(name='Tech Guinée', defaults={'email': 'ventes@techguinee.com', 'phone': '+224 664 98 76 54'})
        sup_digital, _ = Supplier.objects.get_or_create(name='Digital Supply', defaults={'email': 'contact@digitalsupply.gn'})

        Customer.objects.get_or_create(name='Client comptoir')

        products = [
            ('Clavier USB', 'P001', cat_informatique, sup_abc, 50000, 70000, 45, 5),
            ('Souris USB', 'P002', cat_informatique, sup_abc, 25000, 40000, 22, 5),
            ('SSD 512 Go', 'P003', cat_stockage, sup_tech, 450000, 550000, 18, 5),
            ('Disque dur 1 To', 'P004', cat_stockage, sup_tech, 380000, 480000, 12, 3),
            ('USB 32 Go', 'P005', cat_stockage, sup_digital, 35000, 55000, 30, 10),
            ('Routeur Wi-Fi', 'P006', cat_reseau, sup_tech, 220000, 320000, 8, 3),
            ('Câble Ethernet', 'P007', cat_reseau, sup_digital, 15000, 25000, 50, 10),
            ('Écran 24 pouces', 'P008', cat_informatique, sup_abc, 800000, 1100000, 6, 2),
        ]
        for name, ref, cat, sup, buy, sell, stock, minimum in products:
            Product.objects.get_or_create(
                reference=ref,
                defaults=dict(name=name, category=cat, supplier=sup, purchase_price=buy,
                               selling_price=sell, stock_quantity=stock, minimum_stock=minimum),
            )

        self.stdout.write(self.style.SUCCESS("✅ Données de démonstration générées avec succès."))
        self.stdout.write("Comptes de test : severin / mamadou / fatou — mot de passe : ChangeMoi123!")

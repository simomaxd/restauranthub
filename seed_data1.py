import sqlite3

def seed_data():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] > 0:
        print("Menu already has data.")
        conn.close()
        return

    items = [
        ('Margherita Pizza', 'بيتزا مارغريتا', 'Pizza Margherita',
         'Classic pizza with tomato, mozzarella, and basil.',
         'بيتزا كلاسيكية مع الطماطم والموزاريلا والريحان.',
         'Pizza classique avec tomate, mozzarella et basilic.',
         12.99, 'Pizza', 'margherita.jpg'),

        ('Pepperoni Pizza', 'بيتزا بيبروني', 'Pizza Pepperoni',
         'Pizza with pepperoni and cheese.',
         'بيتزا مع البيبروني والجبن.',
         'Pizza avec pepperoni et fromage.',
         14.99, 'Pizza', 'pepperoni.jpg'),

        ('Spaghetti Carbonara', 'سباغيتي كاربونارا', 'Spaghetti Carbonara',
         'Pasta with eggs, cheese, and pancetta.',
         'معكرونة مع البيض والجبن.',
         'Pâtes aux œufs, fromage et pancetta.',
         13.99, 'Pasta', 'carbonara.jpg'),

        ('Caesar Salad', 'سلطة سيزر', 'Salade César',
         'Fresh salad with chicken, croutons, and parmesan.',
         'سلطة طازجة مع الدجاج والخبز المحمص والبارميزان.',
         'Salade fraîche avec poulet, croûtons et parmesan.',
         9.99, 'Salad', 'caesar-salad.jpg'),

        ('Classic Burger', 'برغر كلاسيكي', 'Burger Classique',
         'Beef burger with lettuce, tomato, and cheese.',
         'برغر لحم بقري مع الخس والطماطم والجبن.',
         'Burger au bœuf avec laitue, tomate et fromage.',
         10.99, 'Burger', 'burger.jpg'),

        ('Chicken Wings', 'أجنحة الدجاج', 'Ailes de Poulet',
         'Spicy chicken wings with dipping sauce.',
         'أجنحة دجاج حارة مع صلصة التغميس.',
         'Ailes de poulet épicées avec sauce.',
         8.99, 'Appetizer', 'chicken-wings.jpg'),

        ('Tiramisu', 'تيراميسو', 'Tiramisu',
         'Classic Italian dessert with coffee and mascarpone.',
         'حلوى إيطالية كلاسيكية مع القهوة والمسكربوني.',
         'Dessert italien classique au café et mascarpone.',
         6.99, 'Dessert', 'tiramisu.jpg'),

        ('Cheesecake', 'تشيز كيك', 'Cheesecake',
         'Creamy cheesecake with berry topping.',
         'تشيز كيك كريمي مع طبقة من التوت.',
         'Cheesecake crémeux avec garniture aux baies.',
         5.99, 'Dessert', 'cheesecake.jpg'),

        ('Cappuccino', 'كابتشينو', 'Cappuccino',
         'Espresso with steamed milk and foam.',
         'إسبريسو مع الحليب المبخر والرغوة.',
         'Espresso avec lait vaporisé et mousse.',
         3.99, 'Drink', 'cappuccino.jpg'),

        ('Fresh Orange Juice', 'عصير برتقال طازج', "Jus d'Orange Frais",
         'Freshly squeezed orange juice.',
         'عصير برتقال طازج.',
         "Jus d'orange fraîchement pressé.",
         4.99, 'Drink', 'orange-juice.jpg')
    ]

    cursor.executemany('''
        INSERT INTO menu (name, name_ar, name_fr, description, description_ar, description_fr, price, category, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', items)

    conn.commit()
    conn.close()
    print("Menu seeded successfully with 10 items.")

if __name__ == '__main__':
    seed_data()
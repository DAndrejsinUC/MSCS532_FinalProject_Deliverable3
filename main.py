from tea import Tea
from customer import Customer
from raw_data import RAW_TEAS

# Load teas from raw data
teas = [Tea(
    tea_id=data["tea_id"],
    name=data["name"],
    kind=data["kind"],
    countries=data["countries"],
    flavors=set(data["flavors"]),
    benefits=set(data["benefits"]),
    caffeine=data["caffeine"]
) for data in RAW_TEAS]

# Create a lookup by tea_id for convenience when simulating interactions
teas_by_id = {t.tea_id: t for t in teas}

# Sample customer 1: answered survey
cust1 = Customer("cust1", "Alice")
cust1.set_survey_preferences(
    kinds=["green"],
    countries=["Japan"],
    flavors=["floral", "umami"],
    benefits=["antioxidants", "mental_clarity"],
    caffeine_levels=["medium"]
)

# Sample customer 2: made two purchases
cust2 = Customer("cust2", "Bob")
# Use the available tea ids from raw data. The Kagoshima sencha id is "sencha_kagoshima".
cust2.add_purchase(teas_by_id["sencha_kagoshima"])
cust2.add_purchase(teas_by_id["matcha"])

# Sample customer 3: clicked 5 teas
cust3 = Customer("cust3", "Charlie")
for tea_id in ["jasmine_pearls", "gyokuro", "dragonwell", "genmaicha", "gunpowder_green"]:
    cust3.add_view(teas_by_id[tea_id])

# Sample customer 4: clicked and purchased
cust4 = Customer("cust4", "Dana")
cust4.add_view(teas_by_id["gyokuro"])
cust4.add_view(teas_by_id["sencha_kagoshima"])
cust4.add_purchase(teas_by_id["gyokuro"])

# Sample customer 5: survey + view
cust5 = Customer("cust5", "Eve")
cust5.set_survey_preferences(
    kinds=["black"],
    countries=["India"],
    flavors=["malty"],
    benefits=["heart_health"],
    caffeine_levels=["high"]
)
# Use the actual tea id present in RAW_TEAS: "assam"
cust5.add_view(teas_by_id["assam"])

# Recommend teas (prints top 3 for each)
for customer in [cust1, cust2, cust3, cust4, cust5]:
    recommendations = customer.recommend_teas(teas, top_n=5)
    print(f"\nTop recommendations for {customer.name}:")
    for tea, score in recommendations:
        print(f"- {tea.name} ({tea.tea_id}) — score: {score}")

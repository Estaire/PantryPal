"""
Curated ingredient substitutions. This file is data only: edit freely, then
run the tests (they validate the whole table when the app imports it).

HOW TO READ IT
    "needed ingredient": [(alternative, quality, note), ...]

    "If a recipe needs <needed ingredient>, you can use <alternative>."

Substitutions are DIRECTIONAL. Margarine can stand in for butter far more
safely than the reverse, so each direction is its own entry. Symmetric pairs
(lemon <-> lime) are declared once in _SYMMETRIC_GROUPS and expanded below;
an explicit entry always wins over a group.

QUALITY (this decides how a swap is treated)
    great  Works in essentially any recipe that uses the ingredient.
           Earns 90% of the ingredient's score and counts as "have it".
    good   Works in most recipes, with a small change in taste, texture or
           method (see the note). Earns 75% and counts as "have it".
    fair   Only works in some contexts (baking only, sauces only, ...) or
           gives a clearly different result. SUGGESTED to the user, but it
           does NOT count as having the ingredient, so it never makes a
           recipe "ready to cook" on its own.

When in doubt, rate lower: a wrong "good" makes the app claim a recipe is
cookable when it isn't.

Names are normalized by recommendations.normalize_ingredient, so plural or
capitalized spellings are fine. Staples (salt, pepper, water, basic oils)
can't be keys here because they are assumed available.

DIETARY TAGS (bottom of the file) describe the plain, unprocessed ingredient.
They are a convenience for filtering suggestions, not an allergen guarantee:
products vary, so users must still check labels.
"""

GREAT = "great"
GOOD = "good"
FAIR = "fair"


_EXPLICIT = {
    # ------------------------------------------------------------------ #
    # Dairy, eggs, and plant milks
    # ------------------------------------------------------------------ #
    "milk": [
        ("soy milk", GREAT, "Use 1:1. Choose unsweetened and plain."),
        ("oat milk", GREAT, "Use 1:1. Slightly sweet and creamy."),
        ("almond milk", GOOD, "Use 1:1. Thinner, with a mild nutty flavor."),
        ("evaporated milk", GOOD, "Dilute with an equal amount of water."),
        ("milk powder", GOOD, "Mix with water following the package directions."),
        ("heavy cream", GOOD, "Mix half cream and half water."),
        ("coconut milk", FAIR, "Richer, with a coconut flavor. Thin with an equal amount of water."),
    ],
    "soy milk": [
        ("milk", GREAT, "Use 1:1. Not dairy-free."),
        ("oat milk", GREAT, "Use 1:1."),
        ("almond milk", GOOD, "Use 1:1. Thinner."),
    ],
    "oat milk": [
        ("milk", GREAT, "Use 1:1. Not dairy-free."),
        ("soy milk", GREAT, "Use 1:1."),
        ("almond milk", GOOD, "Use 1:1. Thinner and less creamy."),
    ],
    "almond milk": [
        ("milk", GOOD, "Use 1:1. Richer. Not dairy-free."),
        ("soy milk", GOOD, "Use 1:1."),
        ("oat milk", GOOD, "Use 1:1. Creamier."),
    ],
    "heavy cream": [
        ("coconut cream", GREAT, "Use 1:1. Adds a coconut flavor."),
        ("evaporated milk", GOOD, "Use 1:1. Lighter, and it will not whip."),
        ("creme fraiche", GOOD, "Use 1:1 in soups and sauces. It will not whip."),
        ("mascarpone", GOOD, "Thin with a splash of milk."),
        ("sour cream", FAIR, "Stir in off the heat so it doesn't curdle. Tangier."),
        ("yogurt", FAIR, "Stir in off the heat so it doesn't split. Tangier and thinner."),
        ("cream cheese", FAIR, "Thin with milk. Tangier."),
        ("milk", FAIR, "Thinner. Fine in soups, not for whipping or rich sauces."),
    ],
    "cream": [
        ("heavy cream", GREAT, "Use 1:1."),
        ("single cream", GREAT, "Use 1:1."),
        ("creme fraiche", GOOD, "Use 1:1."),
        ("milk", FAIR, "Thinner. Fine in soups, not for whipping."),
    ],
    "single cream": [
        ("heavy cream", GOOD, "Mix half heavy cream and half milk."),
        ("milk", FAIR, "Thinner and less rich."),
    ],
    "sour cream": [
        ("yogurt", GREAT, "Use 1:1. Plain, full-fat works best."),
        ("cream cheese", FAIR, "Thin with milk to the right consistency."),
    ],
    "yogurt": [
        ("sour cream", GOOD, "Use 1:1. Richer and less tangy."),
        ("creme fraiche", GOOD, "Use 1:1."),
        ("buttermilk", FAIR, "Thinner. Works in baking and marinades."),
    ],
    "buttermilk": [
        ("milk", GOOD, "Add 1 tbsp lemon juice or white vinegar per cup. Rest 5 minutes."),
        ("yogurt", GOOD, "Thin ¾ cup yogurt with ¼ cup milk per cup."),
        ("sour cream", FAIR, "Thin with milk to the right consistency."),
    ],
    "cream cheese": [
        ("mascarpone", GREAT, "Use 1:1. Richer and less tangy."),
        ("ricotta", FAIR, "Drain well. Softer and less tangy."),
        ("yogurt", FAIR, "Strain through a cloth for dips and spreads, not baking."),
    ],
    "creme fraiche": [
        ("heavy cream", FAIR, "Add a squeeze of lemon juice. Thinner."),
        ("yogurt", FAIR, "Use 1:1 in cold dishes. Thinner."),
    ],
    "mascarpone": [
        ("cream cheese", GOOD, "Use 1:1. Tangier and less rich."),
        ("ricotta", FAIR, "Drain and beat in a little cream."),
    ],
    "ricotta": [
        ("cottage cheese", GOOD, "Drain and blend until smooth."),
        ("mascarpone", FAIR, "Richer and sweeter."),
    ],
    "coconut milk": [
        ("coconut cream", GOOD, "Thin with an equal amount of water."),
        ("heavy cream", FAIR, "Thin with water. Lacks the coconut flavor."),
        ("milk", FAIR, "Thinner. Lacks the coconut flavor."),
    ],
    "coconut cream": [
        ("coconut milk", FAIR, "Chill the can and use the solid top, or simmer to reduce."),
        ("heavy cream", FAIR, "Lacks the coconut flavor."),
    ],
    "evaporated milk": [
        ("milk", FAIR, "Simmer to reduce by about 40%. Less rich."),
        ("heavy cream", FAIR, "Thin with a little water."),
    ],
    "parmesan": [
        ("pecorino", GREAT, "Use 1:1. Saltier, so go easy on added salt."),
        ("nutritional yeast", FAIR, "Use in sauces and toppings. Vegan; lacks the sharpness."),
    ],
    "pecorino": [
        ("parmesan", GREAT, "Use 1:1. Milder and less salty."),
    ],
    "mozzarella": [
        ("provolone", GOOD, "Use 1:1. Melts well, with a sharper flavor."),
        ("monterey jack", GOOD, "Use 1:1. Melts well."),
        ("cheddar", FAIR, "Sharper and oilier when melted."),
    ],
    "cheddar": [
        ("gouda", GOOD, "Use 1:1. Milder and creamier."),
        ("gruyere", GOOD, "Use 1:1. Nuttier."),
        ("mozzarella", FAIR, "Much milder, but melts well."),
    ],
    "feta": [
        ("goat cheese", GOOD, "Crumble it. Creamier and tangier."),
        ("ricotta salata", GREAT, "Use 1:1."),
        ("cottage cheese", FAIR, "Drain well and add salt. Much milder."),
    ],
    "goat cheese": [
        ("feta", GOOD, "Use 1:1. Saltier and firmer."),
        ("cream cheese", FAIR, "Milder. Add a squeeze of lemon."),
    ],
    "egg": [
        ("applesauce", FAIR, "Use ¼ cup per egg. Baking only."),
        ("banana", FAIR, "Mash ½ banana per egg. Baking only; adds banana flavor."),
        ("flaxseed", FAIR, "Mix 1 tbsp ground flaxseed with 3 tbsp water per egg. Baking only."),
        ("chia seed", FAIR, "Mix 1 tbsp chia with 3 tbsp water per egg. Baking only."),
        ("tofu", FAIR, "Blend ¼ cup silken tofu per egg. For baking or scrambles."),
    ],
    "egg yolk": [
        ("egg", FAIR, "Use 1 whole egg for 2 yolks in baking. Less rich."),
    ],

    # ------------------------------------------------------------------ #
    # Fats
    # ------------------------------------------------------------------ #
    "butter": [
        ("margarine", GREAT, "Use 1:1. Choose a firm stick margarine for baking."),
        ("ghee", GREAT, "Use 1:1. Higher smoke point, with a nutty flavor."),
        ("coconut oil", GOOD, "Use 1:1. Solid at room temperature, with a mild coconut taste."),
        ("shortening", GOOD, "Use 1:1. No butter flavor, so add a pinch of salt."),
        ("olive oil", FAIR, "Use about ¾ the amount. Fine for sautéing, not for pastry or frosting."),
        ("vegetable oil", FAIR, "Use about ¾ the amount. Fine for sautéing, not for pastry or frosting."),
    ],
    "margarine": [
        ("butter", GREAT, "Use 1:1."),
        ("shortening", GOOD, "Use 1:1. No butter flavor."),
    ],
    "ghee": [
        ("butter", GREAT, "Use 1:1. Lower smoke point, so avoid high-heat searing."),
    ],
    "shortening": [
        ("lard", GREAT, "Use 1:1."),
        ("butter", GOOD, "Use 1:1. More flavor, slightly less flaky."),
        ("margarine", GOOD, "Use 1:1."),
    ],
    "lard": [
        ("shortening", GREAT, "Use 1:1."),
        ("butter", GOOD, "Use 1:1. Richer flavor, slightly less flaky."),
    ],
    "coconut oil": [
        ("butter", GOOD, "Use 1:1."),
        ("margarine", GOOD, "Use 1:1."),
    ],

    # ------------------------------------------------------------------ #
    # Sweeteners
    # ------------------------------------------------------------------ #
    "sugar": [
        ("brown sugar", GREAT, "Use 1:1. Slightly moister, with a caramel flavor."),
        ("coconut sugar", GREAT, "Use 1:1. Slight caramel flavor."),
        ("honey", GOOD, "Use ¾ the amount and reduce other liquid slightly."),
        ("maple syrup", GOOD, "Use ¾ the amount and reduce other liquid slightly."),
        ("agave", GOOD, "Use ⅔ the amount and reduce other liquid slightly."),
        ("icing sugar", FAIR, "Weigh it instead of measuring by volume. Dissolves fast; fine for drinks and glazes."),
    ],
    "brown sugar": [
        ("coconut sugar", GREAT, "Use 1:1."),
        ("sugar", GOOD, "Use 1:1. For more flavor, add 1 tbsp molasses per cup."),
        ("maple syrup", FAIR, "Use ¾ the amount and reduce other liquid."),
        ("honey", FAIR, "Use ¾ the amount and reduce other liquid."),
    ],
    "icing sugar": [
        ("sugar", GOOD, "Blitz in a blender until powdery. Add 1 tsp cornstarch per cup."),
    ],
    "honey": [
        ("maple syrup", GOOD, "Use 1:1. Different flavor."),
        ("agave", GREAT, "Use 1:1."),
        ("golden syrup", GREAT, "Use 1:1."),
        ("sugar", FAIR, "Dissolve 1¼ cups sugar in ¼ cup water per cup of honey."),
    ],
    "maple syrup": [
        ("agave", GREAT, "Use 1:1."),
        ("honey", GOOD, "Use 1:1. Different flavor."),
        ("golden syrup", GOOD, "Use 1:1. Thinner, with its own flavor."),
        ("brown sugar", FAIR, "Dissolve 1 cup sugar in ¼ cup water per cup of syrup."),
    ],
    "agave": [
        ("honey", GREAT, "Use 1:1."),
        ("maple syrup", GREAT, "Use 1:1."),
    ],
    "golden syrup": [
        ("honey", GREAT, "Use 1:1."),
        ("corn syrup", GREAT, "Use 1:1."),
        ("maple syrup", GOOD, "Use 1:1. Thinner, with its own flavor."),
    ],
    "molasses": [
        ("golden syrup", FAIR, "Milder and sweeter. Use 1:1."),
        ("maple syrup", FAIR, "Milder and sweeter. Use 1:1."),
    ],

    # ------------------------------------------------------------------ #
    # Flours, starches, leaveners, crumbs
    # ------------------------------------------------------------------ #
    "flour": [
        ("bread flour", GREAT, "Use 1:1. Slightly chewier."),
        ("self raising flour", GOOD, "Omit the baking powder and salt from the recipe."),
        ("wholemeal flour", GOOD, "Denser and nuttier. Replace up to half for a lighter result."),
        ("spelt flour", GOOD, "Use 1:1. Nuttier; handle the dough gently."),
        ("gluten free flour", GOOD, "Use a 1:1 blend. Texture varies by brand."),
        ("cornstarch", FAIR, "For thickening only. Use half the amount."),
    ],
    "self raising flour": [
        ("flour", GOOD, "Add 1½ tsp baking powder and ¼ tsp salt per cup of flour."),
    ],
    "bread flour": [
        ("flour", GREAT, "Use 1:1. Slightly less chewy."),
    ],
    "wholemeal flour": [
        ("flour", GREAT, "Use 1:1. Lighter result."),
        ("spelt flour", GREAT, "Use 1:1."),
    ],
    "cornstarch": [
        ("flour", GOOD, "Use 2 tbsp flour per 1 tbsp cornstarch and cook out the raw taste."),
    ],
    "baking powder": [
        ("baking soda", FAIR, "Use ¼ tsp baking soda plus ½ tsp cream of tartar per tsp of baking powder."),
    ],
    "baking soda": [
        ("baking powder", FAIR, "Use 3 times as much. May taste slightly bitter."),
    ],
    "cream of tartar": [
        ("lemon juice", GOOD, "Use 2 tsp per 1 tsp."),
        ("white vinegar", GOOD, "Use 2 tsp per 1 tsp."),
    ],
    "breadcrumb": [
        ("bread", GREAT, "Toast stale bread and blitz it into crumbs."),
        ("oat", FAIR, "Pulse rolled oats. Works in meatballs and toppings."),
    ],
    "cornmeal": [
        ("polenta", GREAT, "Use 1:1. Slightly coarser."),
        ("semolina", FAIR, "Finer. Fine for coating."),
    ],
    "polenta": [
        ("cornmeal", GOOD, "Use 1:1. Finer, so it cooks faster."),
    ],
    "gelatine": [
        ("agar agar", FAIR, "Follow the package, usually about 1 tsp agar per tbsp of gelatine. Sets firmer."),
    ],

    # ------------------------------------------------------------------ #
    # Acids and citrus
    # ------------------------------------------------------------------ #
    "lemon": [
        ("lime", GREAT, "Use 1:1 for juice or zest."),
        ("lemon juice", GOOD, "Use 3 tbsp per lemon. Skip if you need the zest."),
    ],
    "lime": [
        ("lemon", GREAT, "Use 1:1 for juice or zest."),
        ("lime juice", GOOD, "Use 2 tbsp per lime. Skip if you need the zest."),
    ],
    "lemon juice": [
        ("lemon", GREAT, "Squeeze fresh: about 3 tbsp per lemon."),
        ("lime", GREAT, "Squeeze fresh: about 2 tbsp per lime."),
        ("white wine vinegar", FAIR, "Use half the amount. Sharper, less fruity."),
    ],
    "lime juice": [
        ("lime", GREAT, "Squeeze fresh: about 2 tbsp per lime."),
        ("lemon", GREAT, "Squeeze fresh: about 3 tbsp per lemon."),
    ],
    "white wine vinegar": [
        ("rice vinegar", GREAT, "Use 1:1. Milder and slightly sweet."),
        ("white vinegar", GOOD, "Use ¾ the amount. Sharper."),
        ("lemon juice", GOOD, "Use 1:1."),
    ],
    "red wine vinegar": [
        ("sherry vinegar", GREAT, "Use 1:1."),
        ("balsamic vinegar", GOOD, "Sweeter and darker. Use slightly less."),
    ],
    "apple cider vinegar": [
        ("rice vinegar", GREAT, "Use 1:1. Milder."),
        ("white vinegar", GOOD, "Use ¾ the amount. Sharper."),
        ("lemon juice", GOOD, "Use 1:1."),
    ],
    "rice vinegar": [
        ("apple cider vinegar", GREAT, "Use 1:1. Slightly fruitier."),
        ("white wine vinegar", GREAT, "Use 1:1. Add a pinch of sugar."),
        ("lemon juice", GOOD, "Use ¾ the amount."),
    ],
    "white vinegar": [
        ("apple cider vinegar", GREAT, "Use 1:1."),
        ("white wine vinegar", GREAT, "Use 1:1."),
        ("lemon juice", GOOD, "Use 1:1."),
    ],
    "balsamic vinegar": [
        ("red wine vinegar", GOOD, "Add ½ tsp sugar per tbsp."),
        ("apple cider vinegar", FAIR, "Add a pinch of sugar. Lighter in color and flavor."),
    ],

    # ------------------------------------------------------------------ #
    # Sauces and condiments
    # ------------------------------------------------------------------ #
    "soy sauce": [
        ("tamari", GREAT, "Use 1:1. Check the label if you need it gluten-free."),
        ("coconut aminos", GOOD, "Use 1:1. Sweeter and less salty, so add a pinch of salt."),
        ("worcestershire sauce", FAIR, "Use half. Tangier and sweeter."),
        ("fish sauce", FAIR, "Use half. Pungent; add a squeeze of lime."),
    ],
    "worcestershire sauce": [
        ("soy sauce", FAIR, "Add a splash of vinegar and a pinch of sugar."),
    ],
    "fish sauce": [
        ("soy sauce", FAIR, "Use 1:1 with a squeeze of lime. Lacks the funk."),
        ("worcestershire sauce", FAIR, "Use half. Sweeter and tangier."),
    ],
    "oyster sauce": [
        ("hoisin sauce", GOOD, "Use 1:1. Sweeter and thicker."),
        ("soy sauce", FAIR, "Add a pinch of sugar and a little cornstarch to thicken."),
    ],
    "hoisin sauce": [
        ("oyster sauce", GOOD, "Use 1:1. Less sweet; add a pinch of sugar."),
        ("barbecue sauce", FAIR, "Use 1:1. Smokier and tangier."),
    ],
    "tomato paste": [
        ("tomato sauce", GOOD, "Use 3 tbsp per tbsp of paste and simmer to thicken."),
        ("passata", GOOD, "Use 3 tbsp per tbsp of paste and simmer to thicken."),
        ("ketchup", FAIR, "Use 2 tbsp per tbsp of paste. Sweeter, so reduce other sugar."),
    ],
    "tomato sauce": [
        ("tomato paste", GOOD, "Thin 1 tbsp paste with 3 tbsp water per ¼ cup of sauce."),
        ("ketchup", FAIR, "Sweeter. Reduce other sugar."),
    ],
    "passata": [
        ("tomato", GOOD, "Blend the tomatoes and simmer to thicken."),
        ("tomato paste", GOOD, "Thin 1 tbsp paste with 3 tbsp water per ¼ cup of passata."),
    ],
    "tomato": [
        ("passata", FAIR, "Smoother, with no chunks. Fine for sauces and soups."),
        ("tomato sauce", FAIR, "Fine for sauces and soups."),
        ("tomato paste", FAIR, "Dilute with water: 1 tbsp paste per ½ cup. Sauces only."),
    ],
    "mayonnaise": [
        ("yogurt", GOOD, "Use 1:1 in dressings, dips, and salads. Tangier."),
        ("sour cream", GOOD, "Use 1:1 in dressings and dips."),
    ],
    "mustard": [
        ("dijon mustard", GREAT, "Use 1:1. Slightly sharper."),
        ("whole grain mustard", GREAT, "Use 1:1."),
        ("english mustard", GOOD, "Much hotter, so use half."),
        ("mustard powder", FAIR, "Mix 1 tsp powder with 1 tsp water per tbsp of prepared mustard."),
    ],
    "dijon mustard": [
        ("mustard", GOOD, "Use 1:1. Milder."),
        ("english mustard", FAIR, "Much hotter. Use a third."),
    ],
    "mustard powder": [
        ("mustard", GOOD, "Use 1 tbsp prepared mustard per tsp of powder."),
    ],
    "horseradish": [
        ("wasabi", GOOD, "Use half the amount. Similar heat."),
    ],
    "olive": [
        ("black olive", GREAT, "Use 1:1."),
        ("green olive", GREAT, "Use 1:1."),
        ("kalamata olive", GREAT, "Use 1:1. Stronger and fruitier."),
    ],
    "black olive": [
        ("olive", GOOD, "Use 1:1."),
    ],
    "green olive": [
        ("olive", GOOD, "Use 1:1."),
    ],
    "caper": [
        ("green olive", FAIR, "Chop finely. Milder and less sharp."),
    ],
    "tahini": [
        ("sunflower seed butter", GOOD, "Use 1:1."),
        ("peanut butter", FAIR, "Use 1:1 in dips and dressings. Stronger flavor."),
        ("almond butter", FAIR, "Use 1:1. Sweeter."),
    ],
    "peanut butter": [
        ("almond butter", GREAT, "Use 1:1."),
        ("sunflower seed butter", GREAT, "Use 1:1. A good nut-free option."),
        ("tahini", GOOD, "Use 1:1 in savory dishes. Add a pinch of sugar."),
    ],
    "almond butter": [
        ("peanut butter", GREAT, "Use 1:1."),
    ],
    "vanilla extract": [
        ("vanilla pod", GREAT, "Scrape the seeds from 1 pod per tbsp of extract."),
        ("vanilla bean paste", GREAT, "Use 1:1."),
        ("almond extract", FAIR, "Use ¼ the amount. Different flavor."),
    ],
    "vanilla pod": [
        ("vanilla extract", GREAT, "Use 1 tbsp extract per pod."),
        ("vanilla bean paste", GREAT, "Use 1 tbsp per pod."),
    ],
    "vanilla bean paste": [
        ("vanilla extract", GREAT, "Use 1:1."),
        ("vanilla pod", GREAT, "Scrape the seeds from 1 pod per tbsp."),
    ],
    "cocoa powder": [
        ("cacao powder", GREAT, "Use 1:1. Slightly more bitter."),
        ("carob powder", GOOD, "Use 1:1. Sweeter, so reduce the sugar."),
        ("dark chocolate", FAIR, "Melt 1 oz per 3 tbsp cocoa and reduce the butter and sugar slightly."),
    ],
    "cacao powder": [
        ("cocoa powder", GREAT, "Use 1:1. Slightly milder."),
    ],
    "dark chocolate": [
        ("milk chocolate", GOOD, "Use 1:1. Sweeter, so reduce the sugar slightly."),
        ("chocolate chip", GOOD, "Use 1:1 by weight. Melts less smoothly."),
        ("cocoa powder", FAIR, "Use 3 tbsp cocoa plus 1 tbsp butter per ounce."),
    ],
    "milk chocolate": [
        ("dark chocolate", GOOD, "Use 1:1. More bitter; add a little sugar."),
        ("chocolate chip", GOOD, "Use 1:1 by weight."),
    ],
    "chocolate chip": [
        ("dark chocolate", GREAT, "Chop into chunks."),
        ("milk chocolate", GREAT, "Chop into chunks."),
    ],

    # ------------------------------------------------------------------ #
    # Spices and dried seasonings
    # ------------------------------------------------------------------ #
    "curry powder": [
        ("garam masala", FAIR, "Milder. Add a pinch of turmeric and cumin."),
    ],
    "garam masala": [
        ("curry powder", FAIR, "Milder and less aromatic. Add a pinch of cinnamon."),
    ],
    "chilli powder": [
        ("cayenne pepper", GOOD, "Hotter, so use ¼ the amount."),
        ("chilli flake", GOOD, "Crush finely. Use 1:1."),
        ("paprika", FAIR, "Milder. Add a pinch of cayenne."),
    ],
    "cayenne pepper": [
        ("chilli powder", GOOD, "Use twice as much, to taste."),
        ("chilli flake", GOOD, "Crush finely. Use 1:1."),
        ("paprika", FAIR, "Much milder. Add a pinch of chilli flakes."),
    ],
    "chilli flake": [
        ("cayenne pepper", GOOD, "Use half the amount."),
        ("chilli powder", GOOD, "Use 1:1. Milder."),
        ("chilli", GOOD, "Finely chop 1 fresh chilli per ½ tsp of flakes."),
    ],
    "paprika": [
        ("smoked paprika", GREAT, "Use 1:1. Adds a smoky flavor."),
        ("chilli powder", FAIR, "Hotter. Use half."),
        ("cayenne pepper", FAIR, "Much hotter. Use ¼ the amount."),
    ],
    "smoked paprika": [
        ("paprika", GOOD, "Use 1:1. Lacks the smoke; add a pinch of cumin."),
    ],
    "chilli": [
        ("jalapeno", GREAT, "Use 1:1. Milder."),
        ("chilli flake", GOOD, "Use ½ tsp per chilli."),
        ("chilli powder", GOOD, "Use ¼ to ½ tsp per chilli."),
        ("cayenne pepper", GOOD, "Use ⅛ tsp per chilli, to taste."),
    ],
    "jalapeno": [
        ("chilli", GOOD, "Use 1:1. Often hotter, so use less."),
    ],
    "cinnamon": [
        ("mixed spice", GOOD, "Use 1:1. A slightly sweeter blend."),
        ("allspice", FAIR, "Use half the amount. Peppery and sweet."),
        ("nutmeg", FAIR, "Use a quarter of the amount."),
    ],
    "mixed spice": [
        ("allspice", GOOD, "Use 1:1. Add a pinch of cinnamon."),
        ("cinnamon", FAIR, "Add a pinch of nutmeg and ginger."),
    ],
    "allspice": [
        ("mixed spice", GOOD, "Use 1:1."),
        ("cinnamon", FAIR, "Use half. Add a pinch of nutmeg and cloves."),
    ],
    "nutmeg": [
        ("mace", GREAT, "Use 1:1."),
        ("allspice", GOOD, "Use 1:1."),
        ("cinnamon", FAIR, "Use half."),
    ],
    "mace": [
        ("nutmeg", GREAT, "Use 1:1. Slightly sweeter."),
    ],
    "clove": [
        ("allspice", GOOD, "Use 1:1."),
    ],
    "ginger": [
        ("ground ginger", GOOD, "Use ¼ tsp ground per 1 tbsp fresh grated."),
        ("galangal", GOOD, "Use 1:1. More citrusy and piney."),
    ],
    "ground ginger": [
        ("ginger", GOOD, "Use 1 tbsp fresh grated per ¼ tsp ground."),
    ],
    "cumin": [
        ("garam masala", FAIR, "Use half. Warmer and sweeter."),
    ],
    "saffron": [
        ("turmeric", FAIR, "Adds color but not the flavor. Use a small pinch."),
    ],
    "turmeric": [
        ("curry powder", FAIR, "Use twice as much. Adds other flavors."),
    ],
    "bay leaf": [
        ("thyme", FAIR, "Use a small pinch. Bay leaf is subtle."),
    ],

    # ------------------------------------------------------------------ #
    # Herbs
    # ------------------------------------------------------------------ #
    "coriander": [
        ("parsley", FAIR, "Milder. Lacks the citrusy flavor."),
    ],
    "parsley": [
        ("chervil", GOOD, "Use 1:1. Milder, with a hint of anise."),
        ("coriander", FAIR, "Stronger and citrusy. Use less."),
    ],
    "basil": [
        ("oregano", FAIR, "Use a third of the amount. More pungent."),
    ],
    "oregano": [
        ("italian seasoning", GOOD, "Use 1:1."),
        ("thyme", GOOD, "Use 1:1. Milder and more lemony."),
        ("basil", FAIR, "Use 1:1. Sweeter."),
    ],
    "marjoram": [
        ("thyme", GOOD, "Use 1:1."),
    ],
    "italian seasoning": [
        ("oregano", GOOD, "Use 1:1. Add a pinch of basil and thyme."),
        ("mixed herb", GREAT, "Use 1:1."),
    ],
    "mixed herb": [
        ("italian seasoning", GREAT, "Use 1:1."),
        ("thyme", GOOD, "Use 1:1."),
        ("oregano", GOOD, "Use 1:1."),
    ],
    "thyme": [
        ("italian seasoning", GOOD, "Use 1:1."),
        ("mixed herb", GOOD, "Use 1:1."),
        ("oregano", GOOD, "Use half. More pungent."),
        ("rosemary", FAIR, "Use half. Stronger and piney."),
    ],
    "rosemary": [
        ("thyme", GOOD, "Use 1:1. Milder."),
        ("sage", GOOD, "Use 1:1."),
        ("oregano", FAIR, "Use half. Milder, less piney."),
    ],
    "sage": [
        ("thyme", GOOD, "Use 1:1. Less earthy."),
        ("marjoram", GOOD, "Use 1:1."),
        ("rosemary", FAIR, "Use half. Stronger."),
    ],
    "mint": [
        ("basil", FAIR, "Use 1:1. Different, but still fresh."),
    ],
    "dill": [
        ("tarragon", GOOD, "Use half. More anise."),
        ("fennel", FAIR, "Use the fronds. Milder anise."),
        ("parsley", FAIR, "Use 1:1. Lacks the distinct flavor."),
    ],
    "tarragon": [
        ("chervil", GOOD, "Use 1:1."),
        ("dill", FAIR, "Use 1:1. Less anise."),
    ],
    "chervil": [
        ("parsley", GOOD, "Use 1:1. Add a pinch of tarragon."),
        ("tarragon", FAIR, "Use half. Stronger anise."),
    ],
    "chives": [
        ("spring onion", GREAT, "Use the green parts, finely sliced."),
    ],

    # ------------------------------------------------------------------ #
    # Onions and alliums
    # ------------------------------------------------------------------ #
    "onion": [
        ("shallot", GREAT, "Use about 3 shallots per medium onion."),
        ("leek", GOOD, "Use the white and pale green parts. Milder."),
        ("spring onion", GOOD, "Use a large bunch. Milder."),
        ("onion powder", FAIR, "Use 1 tbsp per medium onion. No texture."),
    ],
    "shallot": [
        ("onion", GREAT, "Use ¼ of a medium onion per shallot."),
        ("spring onion", GOOD, "Use the white parts. Milder."),
    ],
    "leek": [
        ("onion", GOOD, "Use ½ onion per leek. Sweeter and stronger."),
        ("spring onion", GOOD, "Use more. Milder."),
    ],
    "spring onion": [
        ("chives", GOOD, "Use more than called for. Milder."),
        ("leek", GOOD, "Use the white and pale green parts, finely sliced."),
        ("shallot", GOOD, "Finely sliced. Milder and sweeter."),
        ("onion", FAIR, "Slice thinly and rinse in cold water to mellow it."),
    ],
    "garlic": [
        ("garlic powder", GOOD, "Use ⅛ tsp per clove."),
        ("garlic granule", GOOD, "Use ¼ tsp per clove."),
    ],
    "garlic powder": [
        ("garlic", GOOD, "Use 1 fresh clove per ⅛ tsp."),
        ("garlic granule", GREAT, "Use twice as much."),
    ],
    "garlic granule": [
        ("garlic powder", GREAT, "Use half the amount."),
        ("garlic", GOOD, "Use 1 clove per ¼ tsp."),
    ],
    "onion powder": [
        ("onion", GOOD, "Use 1 small onion, finely chopped, per tbsp of powder."),
    ],

    # ------------------------------------------------------------------ #
    # Vegetables
    # ------------------------------------------------------------------ #
    "potato": [
        ("sweet potato", GOOD, "Sweeter and softer. Shorten the cooking time."),
        ("parsnip", FAIR, "Sweeter. Works roasted or mashed."),
        ("celeriac", FAIR, "Earthier. Works roasted or mashed."),
    ],
    "sweet potato": [
        ("potato", GOOD, "Less sweet and slightly firmer."),
        ("carrot", FAIR, "Works in soups and mash. Cooks faster."),
    ],
    "carrot": [
        ("parsnip", GOOD, "Sweeter and earthier. Cooks in about the same time."),
        ("sweet potato", FAIR, "Softer and sweeter. Cooks faster."),
        ("butternut squash", FAIR, "Softer. Better in soups and roasts than raw."),
    ],
    "parsnip": [
        ("carrot", GOOD, "Less sweet and less earthy."),
        ("turnip", GOOD, "Slightly peppery."),
        ("celeriac", GOOD, "Earthier and less sweet."),
    ],
    "turnip": [
        ("parsnip", GOOD, "Sweeter and softer."),
    ],
    "cabbage": [
        ("kale", GOOD, "Slice thinly and cook a little longer."),
        ("red cabbage", GOOD, "The color will bleed into the dish."),
        ("bok choy", FAIR, "Milder and quicker to cook."),
    ],
    "kale": [
        ("cavolo nero", GREAT, "Use 1:1."),
        ("collard green", GREAT, "Use 1:1."),
        ("spinach", GOOD, "Cooks much faster. Add at the end."),
        ("cabbage", GOOD, "Slice thinly and cook a little longer."),
        ("chard", GOOD, "Use 1:1. Cooks faster."),
    ],
    "spinach": [
        ("chard", GOOD, "Use 1:1. Cook a little longer."),
        ("kale", GOOD, "Remove the stems and cook longer."),
        ("rocket", FAIR, "Peppery. Best raw or wilted at the end."),
    ],
    "chard": [
        ("spinach", GOOD, "Use 1:1. Cooks faster."),
        ("kale", GOOD, "Remove the stems and cook longer."),
    ],
    "lettuce": [
        ("romaine lettuce", GREAT, "Use 1:1."),
        ("iceberg lettuce", GREAT, "Use 1:1. Crunchier and milder."),
        ("little gem lettuce", GREAT, "Use 1:1."),
        ("rocket", FAIR, "Peppery. Good in salads."),
        ("spinach", FAIR, "Baby spinach works in salads and sandwiches."),
    ],
    "rocket": [
        ("watercress", GREAT, "Use 1:1. Peppery."),
        ("spinach", GOOD, "Milder. Add a squeeze of lemon."),
    ],
    "watercress": [
        ("rocket", GREAT, "Use 1:1. Slightly milder."),
    ],
    "cauliflower": [
        ("broccoli", GOOD, "Cook slightly less."),
    ],
    "broccoli": [
        ("cauliflower", GOOD, "Cook slightly longer."),
    ],
    "green bean": [
        ("snow pea", GOOD, "Cook for less time."),
        ("asparagus", GOOD, "Cut into lengths and cook for less time."),
        ("broccoli", FAIR, "Cut into small florets."),
    ],
    "asparagus": [
        ("green bean", GOOD, "Cook slightly longer."),
        ("broccoli", FAIR, "Use the stems and florets."),
    ],
    "snow pea": [
        ("green bean", GOOD, "Cook slightly longer."),
    ],
    "eggplant": [
        ("zucchini", GOOD, "Softer and quicker to cook. No need to salt."),
        ("mushroom", FAIR, "Meaty texture. Use large caps."),
    ],
    "cucumber": [
        ("zucchini", FAIR, "Raw and thinly sliced. Milder."),
    ],
    "mushroom": [
        ("portobello mushroom", GREAT, "Use 1:1. Larger and meatier."),
        ("shiitake mushroom", GOOD, "Stronger flavor. Remove the tough stems."),
        ("oyster mushroom", GOOD, "Use 1:1. Delicate and quick to cook."),
    ],
    "celery": [
        ("fennel", GOOD, "Use the bulb, thinly sliced. Mild anise flavor."),
        ("celeriac", FAIR, "Cooked dishes only."),
    ],
    "fennel": [
        ("celery", FAIR, "Lacks the anise flavor. Add a pinch of fennel seed."),
    ],

    # ------------------------------------------------------------------ #
    # Fruit, dried fruit, and nuts
    # ------------------------------------------------------------------ #
    "dried cranberry": [
        ("dried cherry", GREAT, "Use 1:1."),
        ("raisin", GOOD, "Use 1:1. Sweeter."),
        ("sultana", GOOD, "Use 1:1. Sweeter."),
    ],
    "apricot": [
        ("peach", GOOD, "Use 1:1. Sweeter and larger."),
    ],
    "peach": [
        ("apricot", GOOD, "Use 1:1. Tarter."),
    ],
    "nectarine": [
        ("apricot", GOOD, "Use 1:1. Tarter."),
    ],
    "walnut": [
        ("hazelnut", GOOD, "Use 1:1. Toast first."),
        ("almond", GOOD, "Use 1:1. Milder."),
    ],
    "pecan": [
        ("hazelnut", GOOD, "Use 1:1. Toast first."),
        ("almond", FAIR, "Use 1:1. Milder."),
    ],
    "almond": [
        ("hazelnut", GOOD, "Use 1:1. Toast first."),
        ("cashew", FAIR, "Softer and sweeter."),
        ("walnut", FAIR, "Use 1:1. More bitter."),
    ],
    "hazelnut": [
        ("almond", GOOD, "Use 1:1. Toast first."),
    ],
    "cashew": [
        ("almond", GOOD, "Use 1:1."),
        ("peanut", GOOD, "Use 1:1. Stronger flavor."),
    ],
    "peanut": [
        ("cashew", GOOD, "Use 1:1. Milder and creamier."),
        ("almond", FAIR, "Use 1:1. Milder."),
    ],
    "pine nut": [
        ("cashew", GOOD, "Use 1:1. Toast lightly."),
        ("almond", GOOD, "Chop and toast."),
    ],

    # ------------------------------------------------------------------ #
    # Beans, lentils, grains, pasta
    # ------------------------------------------------------------------ #
    "chickpea": [
        ("cannellini bean", GOOD, "Softer and creamier. Cook briefly."),
        ("butter bean", GOOD, "Softer and creamier."),
        ("haricot bean", GOOD, "Softer."),
        ("kidney bean", FAIR, "Different flavor and color."),
    ],
    "cannellini bean": [
        ("chickpea", FAIR, "Firmer, with a nuttier flavor."),
    ],
    "lentil": [
        ("red lentil", GOOD, "Cooks faster and falls apart. Best in soups and dals."),
    ],
    "green lentil": [
        ("red lentil", FAIR, "Falls apart instead of holding its shape. Cooks faster."),
    ],
    "red lentil": [
        ("split pea", GOOD, "Takes longer to cook."),
        ("lentil", FAIR, "Holds its shape and cooks slower."),
    ],
    "split pea": [
        ("red lentil", GOOD, "Cooks much faster. Reduce the time."),
        ("lentil", FAIR, "Holds its shape better."),
    ],
    "quinoa": [
        ("couscous", GOOD, "Cook per the package. Fluffier."),
        ("bulgur", GOOD, "Soak or cook per the package."),
        ("millet", GOOD, "Cook per the package."),
        ("rice", FAIR, "Different texture. Cook per the package."),
    ],
    "couscous": [
        ("bulgur", GOOD, "Soak per the package."),
        ("quinoa", GOOD, "Cook per the package."),
        ("rice", FAIR, "Cook per the package. Heavier."),
    ],
    "bulgur": [
        ("couscous", GOOD, "Soak per the package."),
        ("quinoa", GOOD, "Cook per the package."),
        ("rice", FAIR, "Cook per the package."),
    ],
    "rice": [
        ("couscous", FAIR, "Cook per the package. Works in pilafs and salads."),
        ("quinoa", FAIR, "Cook per the package. Works in bowls and pilafs."),
        ("bulgur", FAIR, "Cook per the package."),
        ("barley", FAIR, "Chewier and slower to cook."),
        ("cauliflower", FAIR, "Rice it in a food processor and cook briefly."),
    ],
    "arborio rice": [
        ("carnaroli rice", GREAT, "Use 1:1. Holds its shape slightly better."),
        ("sushi rice", GOOD, "Use 1:1. Stir less."),
        ("pudding rice", FAIR, "Use 1:1. Starchy; good for creamy dishes."),
    ],
    "carnaroli rice": [
        ("arborio rice", GREAT, "Use 1:1."),
    ],
    "pasta": [
        ("noodle", GOOD, "Egg noodles work in most sauces. Adjust the cooking time."),
        ("egg noodle", GOOD, "Use 1:1. Adjust the cooking time."),
        ("rice noodle", FAIR, "Gluten-free and softer. Adjust the cooking time."),
    ],
    "noodle": [
        ("egg noodle", GREAT, "Use 1:1."),
        ("pasta", GOOD, "Thin spaghetti works in soups and stir-fries."),
        ("rice noodle", GOOD, "Use 1:1. Softer; adjust the cooking time."),
    ],
    "egg noodle": [
        ("noodle", GREAT, "Use 1:1."),
        ("pasta", GOOD, "Use 1:1. Adjust the cooking time."),
    ],
    "rice noodle": [
        ("noodle", FAIR, "Contains wheat or egg. Adjust the cooking time."),
    ],

    # ------------------------------------------------------------------ #
    # Stock, wine, and spirits
    # ------------------------------------------------------------------ #
    "chicken stock": [
        ("vegetable stock", GREAT, "Use 1:1. Milder."),
        ("beef stock", GOOD, "Use 1:1. Darker and richer."),
    ],
    "beef stock": [
        ("chicken stock", GOOD, "Use 1:1. Add a splash of soy sauce for depth."),
        ("vegetable stock", GOOD, "Use 1:1. Add a splash of soy sauce for depth."),
    ],
    "vegetable stock": [
        ("chicken stock", GREAT, "Use 1:1. Not vegetarian."),
        ("beef stock", GOOD, "Use 1:1. Darker and richer. Not vegetarian."),
    ],
    "fish stock": [
        ("vegetable stock", GOOD, "Use 1:1. Add a splash of white wine."),
        ("chicken stock", FAIR, "Use 1:1. Heavier flavor."),
    ],
    "white wine": [
        ("dry vermouth", GREAT, "Use 1:1."),
        ("chicken stock", GOOD, "Use 1:1. Add a splash of lemon juice."),
        ("vegetable stock", GOOD, "Use 1:1. Add a splash of vinegar."),
        ("dry sherry", GOOD, "Use 1:1. Nuttier and sweeter."),
        ("white wine vinegar", FAIR, "Dilute 1 tbsp with 3 tbsp water per ¼ cup."),
        ("apple juice", FAIR, "Sweeter. Add a splash of vinegar."),
    ],
    "red wine": [
        ("port", GOOD, "Sweeter, so use a little less."),
        ("beef stock", GOOD, "Use 1:1. Add a splash of red wine vinegar."),
        ("vegetable stock", FAIR, "Use 1:1. Add a splash of red wine vinegar."),
        ("grape juice", FAIR, "Use unsweetened. Add a splash of vinegar."),
        ("balsamic vinegar", FAIR, "Dilute 1 tbsp with 3 tbsp water per ¼ cup."),
    ],
    "rice wine": [
        ("dry sherry", GOOD, "Use 1:1."),
        ("mirin", FAIR, "Sweeter. Reduce other sugar."),
        ("white wine", FAIR, "Use 1:1. Add a pinch of sugar."),
    ],
    "mirin": [
        ("rice wine", GOOD, "Use 1:1. Add a pinch of sugar."),
        ("dry sherry", GOOD, "Use 1:1. Add a pinch of sugar."),
        ("rice vinegar", FAIR, "Add ½ tsp sugar per tbsp."),
        ("white wine", FAIR, "Add a pinch of sugar."),
    ],
    "dry sherry": [
        ("dry vermouth", GOOD, "Use 1:1. More herbal."),
    ],
    "brandy": [
        ("cognac", GREAT, "Use 1:1."),
        ("rum", FAIR, "Use 1:1. Sweeter."),
        ("whisky", FAIR, "Use 1:1."),
    ],
    "cognac": [
        ("brandy", GREAT, "Use 1:1."),
    ],

    # ------------------------------------------------------------------ #
    # Meat, poultry, and fish
    # ------------------------------------------------------------------ #
    "chicken": [
        ("pork", FAIR, "Adjust the cooking time. Fine in stir-fries and stews."),
        ("tofu", FAIR, "Press and cube. Vegetarian."),
        ("chickpea", FAIR, "Vegetarian. Works in curries and stews."),
    ],
    "turkey": [
        ("pork", FAIR, "Adjust the cooking time."),
    ],
    "pork": [
        ("chicken", GOOD, "Cooks faster. Watch for dryness."),
        ("turkey", GOOD, "Cooks faster. Watch for dryness."),
        ("tofu", FAIR, "Press and cube. Vegetarian."),
    ],
    "beef": [
        ("lamb", GOOD, "Stronger flavor. Cooking time is similar."),
        ("pork", FAIR, "Milder and fattier."),
        ("mushroom", FAIR, "Use meaty mushrooms in stews and sauces."),
        ("lentil", FAIR, "Vegetarian. Works in stews and chilli."),
    ],
    "lamb": [
        ("beef", GOOD, "Milder flavor. Cooking time is similar."),
        ("pork", FAIR, "Milder."),
    ],
    "ground beef": [
        ("ground turkey", GOOD, "Leaner. Add a splash of oil."),
        ("ground chicken", GOOD, "Leaner. Add a splash of oil."),
        ("ground lamb", GOOD, "Stronger flavor."),
        ("lentil", FAIR, "Use 1 cup cooked lentils per ½ lb. Vegetarian; good in sauces and tacos."),
        ("mushroom", FAIR, "Chop finely and cook off the moisture. Best in sauces and tacos."),
    ],
    "ground lamb": [
        ("ground beef", GOOD, "Milder. Add cumin and mint for a lamb-like flavor."),
        ("ground pork", GOOD, "Milder and fattier."),
    ],
    "ground pork": [
        ("ground turkey", GOOD, "Leaner, so add a little oil."),
        ("ground chicken", GOOD, "Leaner, so add a little oil."),
    ],
    "ground turkey": [
        ("ground beef", GOOD, "Fattier and richer."),
        ("ground pork", GOOD, "Fattier and richer."),
    ],
    "ground chicken": [
        ("ground beef", GOOD, "Fattier and richer."),
        ("ground pork", GOOD, "Fattier and richer."),
    ],
    "bacon": [
        ("turkey bacon", GREAT, "Use 1:1. Leaner, so add a little oil."),
        ("ham", GOOD, "Dice and fry until crisp."),
        ("prosciutto", GOOD, "Fry until crisp. Saltier."),
        ("chorizo", FAIR, "Spicy and smoky. Use about half."),
    ],
    "pancetta": [
        ("prosciutto", GOOD, "Use 1:1. Saltier and silkier. Fry until crisp."),
        ("ham", GOOD, "Dice and fry until crisp."),
    ],
    "ham": [
        ("gammon", GREAT, "Use 1:1."),
        ("prosciutto", GOOD, "Use 1:1. Saltier."),
        ("bacon", FAIR, "Smokier and fattier."),
    ],
    "sausage": [
        ("chorizo", GOOD, "Spicier and more heavily seasoned."),
        ("ground pork", FAIR, "Add fennel seed, sage, and garlic. Shape into patties."),
    ],
    "chorizo": [
        ("sausage", FAIR, "Add smoked paprika, garlic, and a pinch of cayenne."),
    ],
    "salmon": [
        ("trout", GREAT, "Use 1:1."),
        ("tuna", FAIR, "Leaner, so cook it less."),
    ],
    "trout": [
        ("salmon", GREAT, "Use 1:1."),
    ],
    "tuna": [
        ("salmon", GOOD, "Canned or cooked salmon works in salads and bakes."),
        ("mackerel", GOOD, "Stronger flavor."),
        ("chickpea", FAIR, "Mash with mayonnaise for a vegan option."),
    ],
    "shrimp": [
        ("scallop", FAIR, "Cooks faster. Sweeter."),
        ("white fish", FAIR, "Use chunks. Milder."),
    ],
    "scallop": [
        ("shrimp", FAIR, "Cooks faster."),
    ],
}


# ("members", quality, note): every ordered pair becomes a directed entry,
# unless an explicit entry above already covers it.
_SYMMETRIC_GROUPS = [
    # Dairy
    (["soy milk", "oat milk"], GREAT, "Use 1:1."),
    (["sour cream", "creme fraiche"], GREAT, "Use 1:1."),
    (["parmesan", "grana padano"], GREAT, "Use 1:1."),
    (["gruyere", "emmental", "comte"], GREAT, "Use 1:1. Gruyère is a little nuttier."),
    (["cheddar", "colby", "monterey jack", "red leicester"], GREAT, "Use 1:1."),
    # Citrus and fruit
    (["lemon", "lime"], GREAT, "Use 1:1 for juice or zest."),
    (["lemon juice", "lime juice"], GREAT, "Use 1:1."),
    (["orange", "tangerine", "clementine", "mandarin"], GREAT, "Use 1:1. Sweeter and easier to peel."),
    (["apple", "pear"], GREAT, "Use 1:1. Cooking time may differ slightly."),
    (["peach", "nectarine"], GREAT, "Use 1:1."),
    (["raisin", "sultana", "currant"], GREAT, "Use 1:1."),
    (["pecan", "walnut"], GREAT, "Use 1:1."),
    # Vinegars, sauces, thickeners
    (["white wine vinegar", "red wine vinegar", "apple cider vinegar"], GREAT, "Use 1:1."),
    (["tomato sauce", "passata"], GREAT, "Use 1:1."),
    (["tamari", "soy sauce"], GREAT, "Use 1:1."),
    (["whole grain mustard", "dijon mustard"], GREAT, "Use 1:1."),
    (["potato starch", "tapioca starch", "arrowroot", "cornstarch"], GREAT, "Use 1:1 for thickening."),
    (["oregano", "marjoram"], GREAT, "Use 1:1. Marjoram is slightly sweeter."),
    (["black olive", "kalamata olive"], GREAT, "Use 1:1. Kalamata are stronger and fruitier."),
    # Vegetables
    (["swede", "turnip"], GREAT, "Use 1:1. Swede is sweeter and denser."),
    (["sweet potato", "butternut squash", "pumpkin"], GREAT, "Use 1:1. Squash is a little less sweet."),
    (["zucchini", "yellow squash"], GREAT, "Use 1:1."),
    (["savoy cabbage", "white cabbage", "cabbage"], GREAT, "Use 1:1."),
    # Beans and lentils
    (["butter bean", "cannellini bean", "haricot bean"], GOOD, "Use 1:1. Butter beans are larger and creamier."),
    (["kidney bean", "black bean", "pinto bean", "borlotti bean"], GREAT, "Use 1:1. Color and creaminess differ slightly."),
    (["green lentil", "brown lentil", "puy lentil", "lentil"], GREAT, "Use 1:1. Puy lentils hold their shape best."),
    # Meat and fish
    (["turkey", "chicken"], GREAT, "Use 1:1. Turkey is leaner, so watch the cooking time."),
    (["ground beef", "ground pork"], GREAT, "Use 1:1. Pork is milder and a little fattier."),
    (["ground turkey", "ground chicken"], GREAT, "Use 1:1. Both are lean, so add a little oil."),
    (["pancetta", "bacon"], GREAT, "Use 1:1. Pancetta is unsmoked; add a pinch of smoked paprika."),
    (["mussel", "clam"], GREAT, "Use 1:1. Cook until the shells open."),
    (["haddock", "cod", "pollock", "hake", "white fish", "tilapia"], GREAT, "Use 1:1. Adjust the cooking time to the thickness."),
]


def _build_rules():
    rules = {needed: list(options) for needed, options in _EXPLICIT.items()}
    taken = {
        needed: {alternative for alternative, _, _ in options}
        for needed, options in _EXPLICIT.items()
    }

    for members, quality, note in _SYMMETRIC_GROUPS:
        for needed in members:
            for alternative in members:
                if alternative == needed:
                    continue

                if alternative in taken.setdefault(needed, set()):
                    continue  # an explicit entry wins

                rules.setdefault(needed, []).append((alternative, quality, note))
                taken[needed].add(alternative)

    return rules


SUBSTITUTION_RULES = _build_rules()


# --------------------------------------------------------------------------- #
# Dietary tags for alternatives (plain, unprocessed form; always check labels)
# --------------------------------------------------------------------------- #

# Plant-based: implies vegetarian, dairy-free and egg-free.
DIET_VEGAN = [
    # plant milks, oils, fats
    "soy milk", "oat milk", "almond milk", "coconut milk", "coconut cream",
    "coconut oil", "olive oil", "vegetable oil",
    # egg replacers, protein, spreads
    "applesauce", "banana", "flaxseed", "chia seed", "tofu", "tahini",
    "sunflower seed butter", "almond butter", "peanut butter",
    "nutritional yeast",
    # sweeteners, starches, sauces
    "maple syrup", "agave", "golden syrup", "coconut sugar", "cornstarch",
    "arrowroot", "potato starch", "tapioca starch", "tamari", "coconut aminos",
    "mustard", "dijon mustard", "whole grain mustard", "mustard powder",
    "cacao powder", "cocoa powder", "carob powder", "vanilla extract",
    "vanilla pod", "vanilla bean paste", "agar agar",
    "lemon", "lime", "lemon juice", "lime juice", "apple cider vinegar",
    "rice vinegar", "white vinegar",
    # legumes and grains
    "chickpea", "cannellini bean", "butter bean", "haricot bean",
    "kidney bean", "black bean", "pinto bean", "borlotti bean", "lentil",
    "green lentil", "brown lentil", "puy lentil", "red lentil", "split pea",
    "quinoa", "couscous", "bulgur", "millet", "barley", "rice",
    "rice noodle", "cornmeal", "polenta", "gluten free flour",
    # vegetables and fruit
    "cauliflower", "broccoli", "mushroom", "portobello mushroom",
    "shiitake mushroom", "oyster mushroom", "potato", "sweet potato",
    "parsnip", "turnip", "swede", "carrot", "celeriac", "kale", "spinach",
    "chard", "cabbage", "savoy cabbage", "white cabbage", "red cabbage",
    "bok choy", "rocket", "watercress", "lettuce", "romaine lettuce",
    "iceberg lettuce", "little gem lettuce", "zucchini", "yellow squash",
    "eggplant", "fennel", "celery", "onion", "shallot", "leek",
    "spring onion", "garlic", "butternut squash", "pumpkin", "green bean",
    "snow pea", "asparagus", "apple", "pear", "peach", "nectarine", "orange",
    "clementine", "tangerine", "mandarin", "raisin", "sultana", "currant",
    "dried cranberry", "dried cherry",
    # nuts and seeds
    "walnut", "pecan", "almond", "hazelnut", "cashew", "peanut", "pine nut",
    # herbs and spices
    "thyme", "oregano", "marjoram", "rosemary", "sage", "mint", "dill",
    "tarragon", "chervil", "parsley", "coriander", "basil", "chives",
    "bay leaf", "cinnamon", "mixed spice", "allspice", "nutmeg", "mace",
    "clove", "ginger", "ground ginger", "galangal", "cumin", "turmeric",
    "saffron", "paprika", "smoked paprika", "chilli powder", "cayenne pepper",
    "chilli flake", "chilli", "jalapeno", "italian seasoning", "mixed herb",
    "curry powder", "garam masala", "garlic powder", "garlic granule",
    "onion powder",
]

# Vegetarian but NOT vegan.
DIET_VEGETARIAN_ONLY = [
    "milk", "evaporated milk", "milk powder", "heavy cream", "cream",
    "single cream", "sour cream", "creme fraiche", "yogurt", "buttermilk",
    "cream cheese", "mascarpone", "ricotta", "cottage cheese", "butter",
    "ghee", "egg", "egg yolk", "honey", "sugar", "brown sugar", "icing sugar",
]

DIET_GLUTEN_FREE = [
    "rice", "quinoa", "millet", "cauliflower", "potato starch", "cornstarch",
    "arrowroot", "tapioca starch", "coconut aminos", "coconut milk",
    "coconut cream", "coconut oil", "maple syrup", "agave", "golden syrup",
    "honey", "tofu", "tahini", "almond butter", "peanut butter",
    "sunflower seed butter", "cornmeal", "polenta", "rice noodle",
    "gluten free flour", "cocoa powder", "cacao powder", "potato",
    "sweet potato", "olive oil", "vegetable oil", "butter", "ghee", "milk",
    "egg", "sugar", "brown sugar",
]

DIET_NUT_FREE = [
    "soy milk", "oat milk", "sunflower seed butter", "tahini", "applesauce",
    "banana", "flaxseed", "chia seed", "tofu", "maple syrup", "agave",
    "honey", "golden syrup", "cornstarch", "arrowroot", "potato starch",
    "tapioca starch", "rice", "quinoa", "millet", "olive oil",
    "vegetable oil", "butter", "ghee", "milk", "heavy cream", "sour cream",
    "yogurt", "egg", "sugar", "brown sugar",
]
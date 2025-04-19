import json
import os


class Categorizer:
    """
    L'objectif de cet objet est de tenir à jour la listes des recette présente dans la db
    """
    def __init__(self, db_name: str="recettes.json"):
        self.db_name = db_name

    def load_recipes_db(self):
        if not os.path.exists(self.db_name) or os.stat(self.db_name).st_size == 0:
            with open(self.db_name, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
        
        with open(self.db_name, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_recipes_db(self, recipes: dict) -> None:
        with open(self.db_name, "w", encoding = "utf-8") as f:
            json.dump(recipes, f, indent = 2, ensure_ascii=False)

    def add_recipe_to_db(self, recipe_name: str, url: str) -> None:
        recipe_db = self.load_recipes_db()
        if recipe_name in recipe_db:
            if not url in recipe_db[recipe_name]:
                print("yep")
                recipe_db[recipe_name].append(url)
        else:
            recipe_db[recipe_name] = [url]
        self.save_recipes_db(recipe_db)


if __name__ == '__main__':

    url1 = "https://www.marmiton.org/recettes/recette_poke-bowl-a-l-hawaienne_344558.aspx"
    url2 = "https://www.marmiton.org/recettes/recette_flan-au-citron-facile_35882.aspx"

    db_name = "recettes.json"
    categorizer = Categorizer(db_name)
    categorizer.add_recipe_to_db("poke bowl", url1)
    categorizer.add_recipe_to_db("flan au citron", url2)




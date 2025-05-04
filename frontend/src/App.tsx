import { useState } from 'react'
import ImageUploader from './ImageUploader';
import IngredientsList from './IngredientsList';
import RecipesList from './RecipesList';
import './App.css'


interface Recipe {
  id: number;
  name: string;
  url: string;
}



function App() {
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<number | null>(null);


  const handleIngredientsUpdate = (newIngredients: string[]) => {
    setIngredients(newIngredients);
    fetchRecipes(newIngredients);
  };

  const fetchRecipes = (ingredients: string[]) => {
    // Ceci est juste un exemple, vous appelleriez votre backend en réalité
    console.log("Recherche de recettes pour:", ingredients);
    setRecipes([
      { id: 1, name: "tiramisu", url: "https://www.marmiton.org/gateaux/voici-la-version-du-tiramisu-que-vous-allez-refaire-tout-l-ete-au-yaourt-et-sans-culpabilite-s4111942.html" },
      { id: 2, name: "gateaux yaourt", url: "https://www.marmiton.org/astuces/les-gateaux-au-yaourt-sortent-plus-moelleux-que-jamais-du-four-si-vous-ajoutez-1-ingredient-simple-a-la-recette-s4108064.html" },
      // D'autres recettes...
    ]);
  };


  const handleIngredientUpdate = (index: number, newValue: string) => {
    const updatedIngredients = [...ingredients];
    updatedIngredients[index] = newValue;
    setIngredients(updatedIngredients);
  };

  const handleIngredientDelete =(index: number) => {
    const updatedIngredidents = ingredients.filter((_, i) => i !== index);
    setIngredients(updatedIngredidents);
  };

  const handleSelectRecipe = (id: number) => {
    setSelectedRecipe(id);
  };

  return (
    <div className="app-container">
      <header>
        <h1>What2Eat</h1>
      </header>
      <main>
        <div className="left-panel">
          <h2>Ingrédients</h2>
          <ImageUploader onIngredientsDetected={handleIngredientsUpdate} />
          <IngredientsList 
            ingredients={ingredients} 
            onIngredientUpdate={handleIngredientUpdate}
            onIngredientDelete={handleIngredientDelete}
          />
        </div>
        <div className="right-panel">
          <RecipesList recipes={recipes} onSelectRecipe={handleSelectRecipe} />
        </div>
      </main>
    </div>
  );
}

export default App;

import React from 'react';
import './RecipesList.css'

interface Recipe {
    id: number;
    name: string;
    url: string;
}


interface RecipesListProps{
    recipes: Recipe[];
    onSelectRecipe: (id:number) => void;
}
const RecipesList: React.FC<RecipesListProps> = ({recipes, onSelectRecipe}) => {
    return (
        <div className = "recipes-panel">
            <h2>Suggested Recipes</h2>
            {recipes.length === 0 ? (
                <p>No recipe found</p>
            ):(
                <div className = "recipes-panel">
                    {recipes.map((recipe) => (
                        <div key={recipe.id} className = "recipe-card" onClick = {
                            () => onSelectRecipe(recipe.id)}>
                            <h3>{recipe.name}</h3>
                            <p>{recipe.url}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default RecipesList;
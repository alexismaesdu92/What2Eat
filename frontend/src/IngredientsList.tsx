import React, {useState} from 'react';




interface IngredientsListProp {
    ingredients:  string[];
    onIngredientUpdate: (index: number, newValue: string) => void;
    onIngredientDelete: (index: number) => void;
    onIngredientAdd: (ingredient: string) => void;
}

const IngredientsList: React.FC<IngredientsListProp> = ({ 
    ingredients, 
    onIngredientUpdate, 
    onIngredientDelete,
    onIngredientAdd 
}) => {
    const[newIngredient, setNewIngredient]= useState('');
    const handleAddIngredient = () => {
        if (newIngredient.trim()) {
            onIngredientAdd(newIngredient.trim());
            setNewIngredient('');
        }
    };
    return (
        <div className = "ingredients-list">
            <h3> Detected Ingredients</h3>
            {ingredients.length === 0 ? (
            <p>No ingredients found. Please Upload new documents</p>
            ) : (
            <ul>
            {ingredients.map((item, index) => (
                <li key={index} className="ingredient-item">
                    <input 
                        type="text"
                        value={item}
                        onChange={(e) => onIngredientUpdate(index, e.target.value)}
                    />
                    <button onClick = {() => onIngredientDelete(index)}>Delete</button>
                </li>
                ))}
            </ul>
        )}
            <div className="add-ingredient">
                <input 
                    type="text"
                    value={newIngredient}
                    onChange={(e) => setNewIngredient(e.target.value)}
                    placeholder="Add new ingredient"
                />
                <button onClick={handleAddIngredient}>Add</button>
            </div>
        </div>
    );
};
    

export default IngredientsList;
    

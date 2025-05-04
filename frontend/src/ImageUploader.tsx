import React, { useState } from 'react';

interface ImageUploaderProps {
    onIngredientsDetected: (ingredients: string[]) => void;
}


const ImageUploader: React.FC<ImageUploaderProps> = ({onIngredientsDetected}) => {
    const [image, setImage] = useState <File | null>(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file && file.type == 'image/png') {
            setImage(file);
        }
        else {
            alert("Merci d'envoyer uniquement des fichiers PNG");
        }
    };
    

    const handleSubmit = async (e:React.FormEvent) => {
        e.preventDefault();
        if (!image) {
            alert('Aucune image selectionnée !');
            return; 
        }
        setLoading(true);
        const formData = new FormData();
        formData.append('image', image);
        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            console.log(result);

            let ingredientsList: string[] = [];
            if (Array.isArray(result)) {
                ingredientsList = result;
            } else if (result.ingredients && Array.isArray(result.ingredients)) {
                ingredientsList = result.ingredients;
            } else {
                const ingredientsText = result.ingredients_text || JSON.stringify(result);
                ingredientsList = ingredientsText
                    .split(',')
                    .map((item: string) => item.trim())
                    .filter((item: string) => item.length > 0);
            }
            onIngredientsDetected(ingredientsList);
            alert(`Ingrédients détectés : ${ingredientsList.join(', ')}`);
        } catch (error) {
            console.error("Error lors de l'upload", error); // Utilisation de error
            alert(`Une erreur s'est produite: ${error instanceof Error ? error.message : String(error)}`);
        } finally {
            setLoading(false);
        }

    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="file" accept="image/png" onChange={handleFileChange} disabled={loading} />
            <br />
            <button type="submit" disabled={loading}>
                {loading ? 'Traitement...' : 'Envoyer l\'image'}
            </button>
            {loading && <p>Analyse en cours...</p>}
        </form>
    );

};

export default ImageUploader;
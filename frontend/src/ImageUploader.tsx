import React, { useState } from 'react';

const ImageUploader: React.FC = () => {
    const [image, setImage] = useState <File | null>(null);


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
        const formData = new FormData();
        formData.append('image', image);


        const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        alert(`Fichier envoyé : ${result.filename || JSON.stringify(result)}`);
        console.log(result);
    };

        return (
            <form onSubmit = {handleSubmit}>
                <input type="file" accept="image/png" onChange={handleFileChange} />
                <br />
                <button type="submit">Envoyer l'image</button>
            </form>
        );

};

export default ImageUploader;
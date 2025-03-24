document.addEventListener('DOMContentLoaded', () => {
    const videoUrlInput = document.getElementById('videoUrl');
    const transcribirBtn = document.getElementById('transcribirBtn');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const transcripcionDiv = document.getElementById('transcripcion');
    const analisisDiv = document.getElementById('analisis');
    const ejemplosDiv = document.getElementById('ejemplos');
    const transcripcionTextoDiv = document.getElementById('transcripcionTexto');
    const analisisTextoDiv = document.getElementById('analisisTexto');
    const ejemplosTextoDiv = document.getElementById('ejemplosTexto');
    const copyButtons = document.querySelectorAll('.copy-button');
    const markdownContentDiv = document.getElementById('markdownContent');
    const markdownTextDiv = document.getElementById('markdownText');

    // Función para validar la URL de YouTube
    function isValidYouTubeUrl(url) {
        try {
            const parsedUrl = new URL(url);
            if (parsedUrl.hostname.includes('youtube.com') || parsedUrl.hostname.includes('youtu.be')) {
                return true;
            }
            return false;
        } catch (e) {
            return false;
        }
    }

    // Función para copiar texto al portapapeles
    function copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        const text = element.innerText || element.textContent;
        navigator.clipboard.writeText(text)
            .then(() => {
                alert('Texto copiado al portapapeles!');
            })
            .catch(err => {
                console.error('Error al copiar el texto: ', err);
                alert('Error al copiar el texto. Por favor, inténtalo manualmente.');
            });
    }

    // Agregar event listeners a los botones de copiar
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.target;
            copyToClipboard(target);
        });
    });

    transcribirBtn.addEventListener('click', async (event) => {
        event.preventDefault();

        // Limpiar los resultados de la búsqueda anterior
        transcripcionTextoDiv.innerHTML = "";
        analisisTextoDiv.querySelector('code').textContent = ""; // Limpiar el contenido de texto plano
        ejemplosTextoDiv.innerHTML = "";
        markdownTextDiv.innerHTML = "";

        const url = videoUrlInput.value;

        // Validar la URL antes de enviar la solicitud
        if (!isValidYouTubeUrl(url)) {
            errorDiv.textContent = 'Por favor, introduce una URL de YouTube válida.';
            errorDiv.classList.remove('hidden');
            return;
        }

        loadingDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        transcripcionDiv.classList.add('hidden');
        analisisDiv.classList.add('hidden');
        ejemplosDiv.classList.add('hidden');
        markdownContentDiv.classList.add('hidden');

        try {
            const response = await fetch('http://localhost:5000/transcribir', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al procesar el video.');
            }

            const data = await response.json();

            // Formatear la transcripción
            transcripcionTextoDiv.innerHTML = data.transcripcion.split('\n').map(p => `<p>${p}</p>`).join('');

            // Mostrar el análisis en formato texto plano
            analisisTextoDiv.querySelector('code').textContent = data.analisis;

            // Mostrar el análisis y los ejemplos de código con resaltado de sintaxis
            ejemplosTextoDiv.querySelector('code').textContent = data.ejemplos;
            Prism.highlightAll();

            // Procesar el contenido markdown y mostrarlo
            markdownTextDiv.innerHTML = marked.parse(data.analisis); // Convertir Markdown a HTML
            markdownContentDiv.classList.remove('hidden');

            transcripcionDiv.classList.remove('hidden');
            analisisDiv.classList.remove('hidden');
            ejemplosDiv.classList.remove('hidden');
            markdownContentDiv.classList.remove('hidden');

        } catch (err) {
            errorDiv.textContent = err.message || 'Error desconocido.';
            errorDiv.classList.remove('hidden');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });
});
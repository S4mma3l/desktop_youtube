// START OF FILE script.js
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

    // URL base de la API
    const API_BASE_URL = 'https://web-production-eab4.up.railway.app'; // O 'http://localhost:5000' para desarrollo local

    // --- Variables de sondeo (polling) ---
    let pollingInterval; // Variable para guardar el temporizador
    const POLLING_DELAY = 8000; // Preguntar cada 8 segundos (ajústalo si es necesario)
    let currentJobId = null; // ID del trabajo actual en proceso
    // ------------------------------------


    function isValidYouTubeUrl(url) {
        // Mantén tu lógica de validación existente
        try {
            const parsedUrl = new URL(url);
            return parsedUrl.hostname.includes('youtube.com') || parsedUrl.hostname.includes('youtu.be');
        } catch (e) {
            return false;
        }
    }

    function copyToClipboard(elementId) {
        // Mantén tu lógica de copiado existente
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Elemento con ID ${elementId} no encontrado para copiar.`);
            return;
        }
        const codeElement = element.querySelector('code');
        const text = codeElement ? codeElement.innerText : (element.innerText || element.textContent);

        navigator.clipboard.writeText(text)
            .then(() => {
                alert('¡Texto copiado al portapapeles!');
            })
            .catch(err => {
                console.error('Error al copiar el texto: ', err);
                alert('Error al copiar el texto. Por favor, inténtalo manualmente.');
            });
    }

    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.target;
            copyToClipboard(target);
        });
    });

    // --- Función para mostrar los resultados ---
    function displayResults(data) {
        // Formatear la transcripción
        transcripcionTextoDiv.innerHTML = (data.transcripcion || "Transcripción no disponible.").split('\n').map(p => `<p>${p}</p>`).join('');

        // Mostrar el análisis en formato texto plano dentro de <code>
        if (analisisTextoDiv && analisisTextoDiv.querySelector('code')) {
            analisisTextoDiv.querySelector('code').textContent = data.analisis || "Análisis no disponible.";
        } else {
            console.error("La estructura del div de texto de análisis es incorrecta.");
        }

        // Mostrar los ejemplos de código con resaltado de sintaxis
        if (ejemplosTextoDiv && ejemplosTextoDiv.querySelector('code')) {
            const codeLangClass = detectLanguage(data.ejemplos) || 'text'; // Detección simple o por defecto
            ejemplosTextoDiv.querySelector('code').className = `language-${codeLangClass}`;
            ejemplosTextoDiv.querySelector('code').textContent = data.ejemplos || "Ejemplos de código no disponibles.";
        } else {
            console.error("La estructura del div de texto de ejemplos es incorrecta.");
        }

        // Procesar el contenido markdown y mostrarlo
        if (data.analisis) {
             markdownTextDiv.innerHTML = marked.parse(data.analisis); // Convertir Markdown a HTML
             markdownContentDiv.classList.remove('hidden');
        } else {
             markdownTextDiv.innerHTML = "<p>Análisis no disponible en formato Markdown.</p>";
             markdownContentDiv.classList.remove('hidden'); // Mostrar mensaje aunque esté vacío
        }

        // Resaltar sintaxis DESPUÉS de establecer el contenido
        Prism.highlightAll();

        // Mostrar secciones de resultados
        transcripcionDiv.classList.remove('hidden');
        analisisDiv.classList.remove('hidden');
        ejemplosDiv.classList.remove('hidden');
        // markdownContentDiv se maneja arriba
    }

    // Heurística simple para detectar lenguaje (muy básica)
    function detectLanguage(code) {
        if (!code) return 'text';
        if (code.match(/<\s*script|function\s*\(|const\s+|let\s+|var\s+/)) return 'javascript';
        if (code.match(/import\s+|def\s+.*:|\w+\(/)) return 'python'; // Suposición muy aproximada
        if (code.match(/<\?php|\$\w+/)) return 'php';
        if (code.match(/public\s+static\s+void\s+main|System\.out\.println/)) return 'java';
        if (code.match(/#include\s*<|int\s+main\(/)) return 'c';
        return 'text'; // Por defecto
    }

    // --- Función para sondear el estado del trabajo ---
    async function pollStatus(jobId) {
        console.log(`Sondeando estado para trabajo ${jobId}...`);
        // Asegurarse de que el indicador de carga siga visible durante el sondeo
        if (loadingDiv.classList.contains('hidden')) {
            loadingDiv.textContent = "Verificando estado...";
            loadingDiv.classList.remove('hidden');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/status/${jobId}`, {
                 method: 'GET',
                 headers: {
                    'Accept': 'application/json',
                    'Origin': window.location.origin // Enviar origen para CORS
                 }
            });

            if (!response.ok) {
                // Manejar 404 Trabajo No Encontrado u otros errores del servidor durante el sondeo
                const errorData = await response.json().catch(() => ({ message: `Error HTTP ${response.status}` })); // Manejo de errores no JSON
                throw new Error(errorData.error || errorData.message || `Error sondeando estado: ${response.statusText} (Estado: ${response.status})`);
            }

            const data = await response.json();

            if (data.status === 'complete') {
                console.log(`Trabajo ${jobId} completado.`);
                clearTimeout(pollingInterval); // Detener sondeo
                loadingDiv.classList.add('hidden'); // Ocultar indicador de carga/procesando
                displayResults(data.data); // Mostrar los datos obtenidos
                currentJobId = null; // Resetear ID de trabajo
            } else if (data.status === 'error') {
                console.error(`Trabajo ${jobId} falló: ${data.message}`);
                clearTimeout(pollingInterval); // Detener sondeo
                loadingDiv.classList.add('hidden');
                errorDiv.textContent = `Error en el procesamiento del servidor: ${data.message || 'Error desconocido.'}`;
                errorDiv.classList.remove('hidden');
                currentJobId = null; // Resetear ID de trabajo
            } else {
                // El estado es 'pending' (pendiente) o 'processing' (procesando)
                console.log(`Trabajo ${jobId} estado: ${data.status}. Sondeando de nuevo en ${POLLING_DELAY/1000}s.`);
                // Actualizar UI para mostrar "Procesando..." si es necesario
                loadingDiv.textContent = `Procesando... (Estado: ${data.status})`; // Dar más feedback
                // Programar el siguiente sondeo
                pollingInterval = setTimeout(() => pollStatus(jobId), POLLING_DELAY);
            }

        } catch (err) {
            console.error('Error durante el fetch de sondeo:', err);
            clearTimeout(pollingInterval); // Detener sondeo en caso de error de fetch
            loadingDiv.classList.add('hidden');
            // Mostrar error de conexión al usuario
            errorDiv.textContent = `Error de conexión al verificar el estado: ${err.message}. Por favor, inténtalo de nuevo más tarde.`;
            errorDiv.classList.remove('hidden');
            currentJobId = null; // Resetear ID de trabajo
        }
    }
    // ------------------------------------------

    transcribirBtn.addEventListener('click', async (event) => {
        event.preventDefault();

        // Detener cualquier sondeo anterior si el usuario hace clic de nuevo
        if (currentJobId) {
             clearTimeout(pollingInterval);
             currentJobId = null;
             console.log("Sondeo anterior detenido.");
        }


        // --- Limpiar resultados anteriores ---
        transcripcionTextoDiv.innerHTML = "";
        if (analisisTextoDiv && analisisTextoDiv.querySelector('code')) {
            analisisTextoDiv.querySelector('code').textContent = "";
        }
        if (ejemplosTextoDiv && ejemplosTextoDiv.querySelector('code')) {
            ejemplosTextoDiv.querySelector('code').textContent = "";
            ejemplosTextoDiv.querySelector('code').className = 'language-text'; // Resetear clase de lenguaje
        }
        markdownTextDiv.innerHTML = "";
        transcripcionDiv.classList.add('hidden');
        analisisDiv.classList.add('hidden');
        ejemplosDiv.classList.add('hidden');
        markdownContentDiv.classList.add('hidden');
        errorDiv.classList.add('hidden'); // Ocultar errores previos
        // ----------------------------------

        const url = videoUrlInput.value;

        if (!isValidYouTubeUrl(url)) {
            errorDiv.textContent = 'Por favor, introduce una URL de YouTube válida.';
            errorDiv.classList.remove('hidden');
            return;
        }

        // --- Mostrar mensaje inicial de carga ---
        loadingDiv.textContent = "Iniciando proceso..."; // Mensaje inicial
        loadingDiv.classList.remove('hidden');
        // ---------------------------------------


        try {
            // --- Solicitud inicial para empezar el trabajo ---
            const response = await fetch(`${API_BASE_URL}/transcribir`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Origin': window.location.origin // Enviar cabecera Origin
                },
                body: JSON.stringify({ url })
            });
            // -------------------------------------------

            // Comprobar si la solicitud inicial fue aceptada (202) o falló (4xx, 5xx)
            if (response.status === 202) {
                const data = await response.json();
                currentJobId = data.job_id;
                console.log(`Trabajo iniciado con ID: ${currentJobId}`);
                // Actualizar mensaje de carga y empezar el sondeo
                loadingDiv.textContent = "Procesando video... Esto puede tardar varios minutos.";
                // Iniciar el sondeo después de un breve retraso inicial
                pollingInterval = setTimeout(() => pollStatus(currentJobId), POLLING_DELAY / 2); // Empezar a sondear antes
            } else {
                 // Manejar errores inmediatos del endpoint /transcribir
                 const errorData = await response.json().catch(() => ({ message: `Error HTTP ${response.status}` })); // Manejo de error no JSON
                 throw new Error(errorData.error || errorData.message || `Error al iniciar el proceso: ${response.statusText} (Estado: ${response.status})`);
            }

        } catch (err) {
            // Manejar errores durante la solicitud fetch inicial (ej. error de red)
            console.error('Error iniciando el trabajo de transcripción:', err);
            loadingDiv.classList.add('hidden');
            errorDiv.textContent = `Error al iniciar: ${err.message || 'Error desconocido.'}`;
            errorDiv.classList.remove('hidden');
            currentJobId = null; // Asegurarse de que no empiece el sondeo
        } finally {
             // No ocultar la carga aquí, el sondeo se encargará de ello
             // Limpiar el input siempre
             videoUrlInput.value = "";
        }
    });
});
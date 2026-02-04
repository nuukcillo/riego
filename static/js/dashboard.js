// static/js/dashboard.js
// Module para gestionar el dashboard de riego

const Dashboard = (() => {
    // Elementos del DOM
    const elements = {
        fechaSelector: null,
        consumoContainer: null,
        consumoSemanalContainer: null,
        fechaSemanalSelector: null,
        fechaMensualSelector: null,
        consumoMensualContainer: null,
        consumoPeriodoContainer: null,
        fechaInicioPeriodoSelector: null,
        fechaFinPeriodoSelector: null
    };

    // Configuración
    const config = {
        apiEndpoint: '/api/consumo-dia',
        apiEndpointSemanal: '/api/consumo-semanal',
        apiEndpointMensual: '/api/consumo-mensual',
        apiEndpointPeriodo: '/api/consumo-periodo',
        dateFormat: 'YYYY-MM-DD'
    };

    /**
     * Inicializa el módulo del dashboard
     */
    const init = () => {
        cacheElements();
        bindEvents();
        setCurrentDate();
    };

    /**
     * Cachea los elementos del DOM
     */
    const cacheElements = () => {
        elements.fechaSelector = document.getElementById('fecha-selector');
        elements.consumoContainer = document.getElementById('consumo-container');
        elements.consumoSemanalContainer = document.getElementById('consumo-semanal-container');
        elements.fechaSemanalSelector = document.getElementById('fecha-semanal-selector');
        elements.fechaMensualSelector = document.getElementById('fecha-mensual-selector');
        elements.consumoMensualContainer = document.getElementById('consumo-mensual-container');
        elements.consumoPeriodoContainer = document.getElementById('consumo-periodo-container');
        elements.fechaInicioPeriodoSelector = document.getElementById('fecha-inicio-periodo');
        elements.fechaFinPeriodoSelector = document.getElementById('fecha-fin-periodo');
    };

    /**
     * Vincula los eventos a los elementos
     */
    const bindEvents = () => {
        if (elements.fechaSelector) {
            elements.fechaSelector.addEventListener('change', (event) => 
                handleDateChange(event, config.apiEndpoint)
            );
        }
        if (elements.fechaSemanalSelector) {
            elements.fechaSemanalSelector.addEventListener('change', (event) => 
                handleDateChange(event, config.apiEndpointSemanal)
            );
        }
        if (elements.fechaMensualSelector) {
            elements.fechaMensualSelector.addEventListener('change', (event) => 
                handleDateChange(event, config.apiEndpointMensual)
            );
        }
        if (elements.fechaInicioPeriodoSelector && elements.fechaFinPeriodoSelector) {
            elements.fechaInicioPeriodoSelector.addEventListener('change', (event) => 
                handlePeriodoChange(event, config.apiEndpointPeriodo)
            );
            elements.fechaFinPeriodoSelector.addEventListener('change', (event) => 
                handlePeriodoChange(event, config.apiEndpointPeriodo)
            );
        }
    };

    /**
     * Establece la fecha actual en el input
     */
    const setCurrentDate = () => {
        if (!elements.fechaSelector) return;

        const hoy = new Date();
        const año = hoy.getFullYear();
        const mes = String(hoy.getMonth() + 1).padStart(2, '0');
        const dia = String(hoy.getDate()).padStart(2, '0');
        
        elements.fechaSelector.value = `${año}-${mes}-${dia}`;
    };

    /**
     * Maneja el cambio de fecha
     */
    const handleDateChange = (event, apiEndpoint = config.apiEndpoint) => {
        const fechaSeleccionada = event.target.value;
        
        if (!fechaSeleccionada) return;
        
        fetchConsumo(fechaSeleccionada, apiEndpoint);
    };

    const handlePeriodoChange = (event, apiEndpoint = config.apiEndpointPeriodo) => {
        const fechaInicio = elements.fechaInicioPeriodoSelector.value;
        const fechaFin = elements.fechaFinPeriodoSelector.value;

        if (!fechaInicio || !fechaFin) return;

        fetchConsumoPeriodo(fechaInicio, fechaFin, apiEndpoint);
    };

    /**
     * Obtiene el consumo de la API para un periodo
     */
    const fetchConsumoPeriodo = (fechaInicio, fechaFin, apiEndpoint) => {
        showLoading();

        fetch(`${apiEndpoint}?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la petición');
                }
                return response.json();  // Cambiar a JSON
            })
            .then(data => {
                renderConsumo(data);  // Pasar el objeto JSON
            })
            .catch(error => {
                console.error('Error:', error);
                showError();
            });
    };

    /**
     * Renderiza el consumo de periodo en el DOM
     */
    const fetchConsumo = (fecha, apiEndpoint) => {
        showLoading();

        fetch(`${apiEndpoint}?fecha=${fecha}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la petición');
                }
                return response.json();  // Cambiar a JSON
            })
            .then(data => {
                renderConsumo(data);  // Pasar el objeto JSON
            })
            .catch(error => {
                console.error('Error:', error);
                showError();
            });
    };

    /**
     * Muestra el estado de carga
     */
    const showLoading = () => {
        if (elements.consumoContainer) {
            elements.consumoContainer.innerHTML =   `<div class="progress"><div class="indeterminate"></div></div>`;
        }
    };

    /**
     * Muestra un mensaje de error
     */
    const showError = () => {
        if (elements.consumoContainer) {
            elements.consumoContainer.innerHTML = '<p class="red-text">Error al cargar datos</p>';
        }
    };

    /**
     * Renderiza el consumo en el DOM
     */
    const renderConsumo = (data) => {
        if (!elements.consumoContainer) return;
        
        // Construir las filas de la tabla
        let filas = '';
        if (data.datos && data.datos.length > 0) {
            data.datos.forEach(row => {
                filas += `
                    <tr>
                        <td>${row.partida}</td>
                        <td>${row.valor}</td>
                    </tr>
                `;
            });
        } else {
            filas = '<tr><td colspan="3" style="text-align: center;">Sin datos</td></tr>';
        }
    
        const html = `
            <table class="responsible-table striped">
                <thead>
                    <tr>
                        <th>Partida</th>
                        <th>Valor</th>
                    </tr>
                </thead>
                <tbody>
                    ${filas}
                </tbody>
            </table>
        `;
        
        elements.consumoContainer.innerHTML = html;
    };
        // API pública
    return {
        init: init
    };
})();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    Dashboard.init();
});
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
        setSelectorsDate();
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
                handleDateChange(event, config.apiEndpoint, elements.consumoContainer)
            );
        }
        if (elements.fechaSemanalSelector) {
            elements.fechaSemanalSelector.addEventListener('change', (event) => 
                handleDateChange(event, config.apiEndpointSemanal, elements.consumoSemanalContainer)
            );
        }
        if (elements.fechaMensualSelector) {
            elements.fechaMensualSelector.addEventListener('change', (event) => 
                handleDateChange(event, config.apiEndpointMensual, elements.consumoMensualContainer)
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
    const numeroDeSemana = fecha => {
        const DIA_EN_MILISEGUNDOS = 1000 * 60 * 60 * 24,
            DIAS_QUE_TIENE_UNA_SEMANA = 7,
            JUEVES = 4;
        fecha = new Date(Date.UTC(fecha.getFullYear(), fecha.getMonth(), fecha.getDate()));
        let diaDeLaSemana = fecha.getUTCDay(); // Domingo es 0, sábado es 6
        if (diaDeLaSemana === 0) {
            diaDeLaSemana = 7;
        }
        fecha.setUTCDate(fecha.getUTCDate() - diaDeLaSemana + JUEVES);
        const inicioDelAño = new Date(Date.UTC(fecha.getUTCFullYear(), 0, 1));
        const diferenciaDeFechasEnMilisegundos = fecha - inicioDelAño;
        return Math.ceil(((diferenciaDeFechasEnMilisegundos / DIA_EN_MILISEGUNDOS) + 1) / DIAS_QUE_TIENE_UNA_SEMANA);
    };
    /**
     * Establece la fecha actual en el input
     */
    const setSelectorsDate = () => {
        if (!elements.fechaSelector) return;

        const hoy = new Date();
        const año = hoy.getFullYear();
        const mes = String(hoy.getMonth() + 1).padStart(2, '0');
        const dia = String(hoy.getDate()).padStart(2, '0');
        const hoyMenos15Dias = new Date(new Date(hoy).setDate(hoy.getDate() - 15));
        const numeroDeSemanaActual = numeroDeSemana(hoy);
        console.log(typeof numeroDeSemanaActual, numeroDeSemanaActual);
        
        elements.fechaSelector.value = `${año}-${mes}-${dia}`;
        elements.fechaSemanalSelector.value = `${año}-W${String(numeroDeSemanaActual).padStart(2, '0')}`;
        elements.fechaMensualSelector.value = `${año}-${mes}`;
        elements.fechaInicioPeriodoSelector.value = `${hoyMenos15Dias.getFullYear()}-${String(hoyMenos15Dias.getMonth() + 1).padStart(2, '0')}-${String(hoyMenos15Dias.getDate()).padStart(2, '0')}`;
        elements.fechaFinPeriodoSelector.value = `${año}-${mes}-${dia}`;
    };

    /**
     * Maneja el cambio de fecha
     */
    const handleDateChange = (event, apiEndpoint = config.apiEndpoint, container = elements.consumoContainer) => {
        const fechaSeleccionada = event.target.value;
        
        if (!fechaSeleccionada) return;
        
        fetchConsumo(fechaSeleccionada, apiEndpoint, container);
    };

    const handlePeriodoChange = (event, apiEndpoint = config.apiEndpointPeriodo) => {
        const fechaInicio = elements.fechaInicioPeriodoSelector.value;
        const fechaFin = elements.fechaFinPeriodoSelector.value;

        if (!fechaInicio || !fechaFin) return;

        fetchConsumoPeriodo(fechaInicio, fechaFin, apiEndpoint, elements.consumoPeriodoContainer);
    };

    /**
     * Obtiene el consumo de la API para un periodo
     */
    const fetchConsumoPeriodo = (fechaInicio, fechaFin, apiEndpoint, container) => {
        showLoading(container);

        fetch(`${apiEndpoint}?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la petición');
                }
                return response.json();  // Cambiar a JSON
            })
            .then(data => {
                renderConsumo(data, container);  // Pasar el objeto JSON
            })
            .catch(error => {
                console.error('Error:', error);
                showError(container);
            });
    };

    /**
     * Renderiza el consumo de periodo en el DOM
     */
    const fetchConsumo = (fecha, apiEndpoint, container) => {
        showLoading(container);

        fetch(`${apiEndpoint}?fecha=${fecha}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la petición');
                }
                return response.json();  // Cambiar a JSON
            })
            .then(data => {
                renderConsumo(data, container);  // Pasar el objeto JSON
            })
            .catch(error => {
                console.error('Error:', error);
                showError(container);
            });
    };

    /**
     * Muestra el estado de carga
     */
    const showLoading = (container = elements.consumoContainer) => {
        if (container) {
            container.innerHTML =   `<div class="progress"><div class="indeterminate"></div></div>`;
        }
    };

    /**
     * Muestra un mensaje de error
     */
    const showError = (container = elements.consumoContainer) => {
        if (container) {
            container.innerHTML = '<p class="red-text">Error al cargar datos</p>';
        }
    };

    /**
     * Renderiza el consumo en el DOM
     */
    const renderConsumo = (data, container = elements.consumoContainer) => {
        if (!container) return;
        
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
        
        container.innerHTML = html;
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
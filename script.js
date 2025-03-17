let scene, camera, renderer, controls;
let simulationData = [];
let particles, surface;
let vizType = 'particles';

function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111133);
    
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(5, 5, 5);
    
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    addCoordinateAxes();
    
    window.addEventListener('resize', onWindowResize, false);
    
    document.getElementById('simulate').addEventListener('click', runSimulation);
    
    const vizRadios = document.querySelectorAll('input[name="vizType"]');
    vizRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            vizType = this.value;
            if (simulationData.length > 0) {
                visualizeData();
            }
        });
    });
    
    animate();
    
    const statusDiv = document.createElement('div');
    statusDiv.id = 'status';
    statusDiv.style.position = 'absolute';
    statusDiv.style.bottom = '10px';
    statusDiv.style.left = '10px';
    statusDiv.style.background = 'rgba(0,0,0,0.5)';
    statusDiv.style.color = 'white';
    statusDiv.style.padding = '5px';
    statusDiv.style.borderRadius = '3px';
    statusDiv.textContent = 'Ready. Click "Run Simulation" to start.';
    document.body.appendChild(statusDiv);
}

function addCoordinateAxes() {
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);
    
    const createLabel = (text, position, color) => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 128;
        canvas.height = 64;
        
        context.fillStyle = 'rgba(255, 255, 255, 0)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        context.font = '48px Arial';
        context.fillStyle = color;
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(text, canvas.width / 2, canvas.height / 2);
        
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        sprite.position.copy(position);
        sprite.scale.set(1, 0.5, 1);
        scene.add(sprite);
    };
    
    createLabel('Time', new THREE.Vector3(5.5, 0, 0), 'red');
    createLabel('Price', new THREE.Vector3(0, 5.5, 0), 'green');
    createLabel('Volatility', new THREE.Vector3(0, 0, 5.5), 'blue');
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function updateStatus(message) {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.textContent = message;
    }
}

function displayAnalytics(data) {
    if (!document.getElementById('analytics-panel')) {
        const panel = document.createElement('div');
        panel.id = 'analytics-panel';
        panel.style.position = 'absolute';
        panel.style.top = '10px';
        panel.style.right = '10px';
        panel.style.width = '300px';
        panel.style.background = 'rgba(255, 255, 255, 0.8)';
        panel.style.padding = '15px';
        panel.style.borderRadius = '5px';
        panel.style.maxHeight = '80vh';
        panel.style.overflowY = 'auto';
        document.body.appendChild(panel);
    }
    
    const panel = document.getElementById('analytics-panel');
    
    let html = `
        <h3>Option Analytics</h3>
        <div class="analytics-section">
            <h4>Option Price</h4>
            <p>${data.option_price.toFixed(4)}</p>
        </div>
        
        <div class="analytics-section">
            <h4>Greeks</h4>
            <table>
                <tr><td>Delta:</td><td>${data.greeks.delta.toFixed(4)}</td></tr>
                <tr><td>Gamma:</td><td>${data.greeks.gamma.toFixed(4)}</td></tr>
                <tr><td>Theta:</td><td>${data.greeks.theta.toFixed(4)}</td></tr>
                <tr><td>Vega:</td><td>${data.greeks.vega.toFixed(4)}</td></tr>
                <tr><td>Rho:</td><td>${data.greeks.rho.toFixed(4)}</td></tr>
            </table>
        </div>
        
        <div class="analytics-section">
            <h4>Risk Metrics</h4>
            <table>
                <tr><td>VaR (95%):</td><td>${data.risk_metrics.var_95.toFixed(4)}</td></tr>
                <tr><td>CVaR (95%):</td><td>${data.risk_metrics.cvar_95.toFixed(4)}</td></tr>
                <tr><td>Max Drawdown:</td><td>${data.risk_metrics.max_drawdown.toFixed(4)}</td></tr>
            </table>
        </div>
        
        <div class="analytics-section">
            <h4>Statistics</h4>
            <table>
                <tr><td>Mean Final Price:</td><td>${data.statistics.mean_final_price.toFixed(2)}</td></tr>
                <tr><td>Std Dev Final Price:</td><td>${data.statistics.std_final_price.toFixed(2)}</td></tr>
                <tr><td>Min Price:</td><td>${data.statistics.min_price.toFixed(2)}</td></tr>
                <tr><td>Max Price:</td><td>${data.statistics.max_price.toFixed(2)}</td></tr>
                <tr><td>Execution Time:</td><td>${data.statistics.execution_time_seconds.toFixed(3)}s</td></tr>
            </table>
        </div>
    `;
    
    panel.innerHTML = html;
}

async function runSimulation() {
    document.getElementById('loading').style.display = 'block';
    updateStatus('Starting simulation...');
    
    const params = {
        initialPrice: parseFloat(document.getElementById('initialPrice').value),
        strikePrice: parseFloat(document.getElementById('strikePrice').value),
        timeToMaturity: parseFloat(document.getElementById('timeToMaturity').value),
        riskFreeRate: parseFloat(document.getElementById('riskFreeRate').value),
        numSimulations: parseInt(document.getElementById('numSimulations').value),
        numSteps: parseInt(document.getElementById('numSteps').value),
        optionType: document.getElementById('optionType').value
    };
    
    console.log('Sending request with params:', params);
    updateStatus('Sending request to server...');
    
    try {
        const response = await fetch('http://localhost:5001/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        
        console.log('Response status:', response.status);
        updateStatus(`Server responded with status: ${response.status}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`Server responded with status ${response.status}: ${errorText}`);
        }
        
        updateStatus('Processing response data...');
        const data = await response.json();
        console.log(`Received ${data.length} data points`);
        
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('Invalid data format received from server');
        }
        
        if (data.visualization_data) {
            simulationData = data.visualization_data;
            displayAnalytics(data);
        } else {
            simulationData = data;
        }
        
        updateStatus(`Visualizing ${data.length} data points...`);
        
        visualizeData();
        updateStatus(`Visualization complete. Showing ${data.length} data points.`);
    } catch (error) {
        console.error('Error running simulation:', error);
        updateStatus(`Error: ${error.message}`);
        alert(`Error running simulation: ${error.message}\nMake sure the Python server is running at http://localhost:5001/`);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function visualizeData() {
    if (particles) scene.remove(particles);
    if (surface) scene.remove(surface);
    
    const timeValues = simulationData.map(d => d.time);
    const priceValues = simulationData.map(d => d.price);
    const volValues = simulationData.map(d => d.volatility);
    
    const maxTime = Math.max(...timeValues);
    const maxPrice = Math.max(...priceValues);
    const maxVol = Math.max(...volValues);
    
    const normalizeData = data => {
        return data.map(d => ({
            x: (d.time / maxTime) * 5,
            y: (d.price / maxPrice) * 5,
            z: (d.volatility / maxVol) * 5,
            originalData: d
        }));
    };
    
    const normalizedData = normalizeData(simulationData);
    
    if (vizType === 'particles') {
        createParticleSystem(normalizedData);
    } else {
        createSurface(normalizedData);
    }
}

function createParticleSystem(data) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(data.length * 3);
    const colors = new Float32Array(data.length * 3);
    
    data.forEach((point, i) => {
        positions[i * 3] = point.x;     
        positions[i * 3 + 1] = point.y;
        positions[i * 3 + 2] = point.z;  
        
        const ratio = point.y / 5;
        colors[i * 3] = 1 - ratio;     
        colors[i * 3 + 1] = ratio;     
        colors[i * 3 + 2] = point.z / 5; 
    });
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const material = new THREE.PointsMaterial({
        size: 0.05,
        vertexColors: true,
        transparent: true,
        opacity: 0.8
    });
    
    particles = new THREE.Points(geometry, material);
    scene.add(particles);
}

function createSurface(data) {
    const timeSteps = [...new Set(data.map(d => d.x))].sort((a, b) => a - b);
    const volSteps = [...new Set(data.map(d => d.z))].sort((a, b) => a - b);
    
    const gridSize = {
        x: timeSteps.length,
        z: volSteps.length
    };
    
    const priceGrid = Array(gridSize.x).fill().map(() => Array(gridSize.z).fill(0));
    const countGrid = Array(gridSize.x).fill().map(() => Array(gridSize.z).fill(0));
    
    data.forEach(point => {
        const xIndex = timeSteps.indexOf(point.x);
        const zIndex = volSteps.indexOf(point.z);
        
        if (xIndex >= 0 && zIndex >= 0) {
            priceGrid[xIndex][zIndex] += point.y;
            countGrid[xIndex][zIndex]++;
        }
    });
    
    for (let i = 0; i < gridSize.x; i++) {
        for (let j = 0; j < gridSize.z; j++) {
            if (countGrid[i][j] > 0) {
                priceGrid[i][j] /= countGrid[i][j];
            }
        }
    }
    
    const geometry = new THREE.PlaneGeometry(5, 5, gridSize.x - 1, gridSize.z - 1);
    
    const positions = geometry.attributes.position.array;
    
    for (let i = 0; i < gridSize.x; i++) {
        for (let j = 0; j < gridSize.z; j++) {
            const index = (i * gridSize.z + j) * 3;
            positions[index] = timeSteps[i];
            positions[index + 1] = priceGrid[i][j];
            positions[index + 2] = volSteps[j];
        }
    }
    
    geometry.computeVertexNormals();
    
    const material = new THREE.MeshPhongMaterial({
        side: THREE.DoubleSide,
        vertexColors: true,
        shininess: 30,
        flatShading: false
    });
    
    const colors = [];
    
    for (let i = 0; i < positions.length; i += 3) {
        const height = positions[i + 1] / 5;
        colors.push(1 - height, height, positions[i + 2] / 5);
    }
    
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    
    surface = new THREE.Mesh(geometry, material);
    scene.add(surface);
}

init(); 
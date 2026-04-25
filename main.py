<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agropecuária Família Vasconcelos - Controle de Produção de Ovos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#4CAF50',
                        secondary: '#8BC34A',
                        accent: '#FFC107',
                        dark: '#388E3C',
                        light: '#DCEDC8',
                    }
                }
            }
        }
    </script>
    <style>
        .logo-preview {
            max-width: 150px;
            max-height: 150px;
        }
        #currentTime {
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-6">
        <!-- Header -->
        <header class="bg-white shadow-md rounded-lg mb-6 p-6 text-center">
            <div id="farmInfo">
                <h1 class="text-4xl font-bold text-primary" id="farmName">Agropecuária Família Vasconcelos</h1>
                <p class="text-xl text-gray-600 mt-2" id="farmSubtitle">Agricultura Familiar - Sítio Sonho Meu</p>
                <p class="text-lg text-gray-500 mt-1" id="farmLocation">Localização: São Gonçalo do Amarante - CE</p>
            </div>
            <div class="mt-4 flex justify-center">
                <img id="logoPreview" class="logo-preview hidden" alt="Logo Preview">
            </div>
            <div class="mt-4 text-right">
                <div class="inline-block bg-gray-200 px-4 py-2 rounded-lg">
                    <span id="currentTime" class="font-bold"></span>
                </div>
            </div>
        </header>

        <!-- Navigation -->
        <nav class="bg-white shadow-md rounded-lg mb-6 overflow-hidden">
            <ul class="flex flex-wrap justify-around">
                <li class="w-full sm:w-auto"><a href="#" onclick="showSection('production')" class="block px-6 py-4 hover:bg-primary hover:text-white font-medium transition"><i class="fas fa-egg mr-2"></i>Registro de Produção Diária</a></li>
                <li class="w-full sm:w-auto"><a href="#" onclick="showSection('dashboard')" class="block px-6 py-4 hover:bg-primary hover:text-white font-medium transition"><i class="fas fa-chart-line mr-2"></i>Dashboard</a></li>
                <li class="w-full sm:w-auto"><a href="#" onclick="showSection('notes')" class="block px-6 py-4 hover:bg-primary hover:text-white font-medium transition"><i class="fas fa-calendar-day mr-2"></i>Anotações</a></li>
                <li class="w-full sm:w-auto"><a href="#" onclick="showSection('settings')" class="block px-6 py-4 hover:bg-primary hover:text-white font-medium transition"><i class="fas fa-cog mr-2"></i>Configurações</a></li>
            </ul>
        </nav>

        <!-- Main Content -->
        <main>
            <!-- Production Section -->
            <section id="production" class="bg-white shadow-md rounded-lg p-6 mb-6">
                <h2 class="text-2xl font-bold text-primary mb-4"><i class="fas fa-egg mr-2"></i>Registro de Produção Diária</h2>
                
                <form id="productionForm" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="shedName" class="block text-gray-700 font-medium mb-2">Nome do Galpão</label>
                            <input type="text" id="shedName" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary" required>
                        </div>
                        <div>
                            <label for="recordDate" class="block text-gray-700 font-medium mb-2">Data do Registro</label>
                            <input type="date" id="recordDate" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary" required>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="goodEggs" class="block text-gray-700 font-medium mb-2">Ovos Úteis</label>
                            <input type="number" id="goodEggs" min="0" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary" required>
                        </div>
                        <div>
                            <label for="brokenEggs" class="block text-gray-700 font-medium mb-2">Ovos Quebrados</label>
                            <input type="number" id="brokenEggs" min="0" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary" required>
                        </div>
                    </div>
                    
                    <div class="flex justify-end space-x-4">
                        <button type="button" onclick="clearProductionForm()" class="px-6 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition">Limpar</button>
                        <button type="submit" class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-dark transition">Salvar Registro</button>
                    </div>
                </form>
                
                <div class="mt-8">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">Registros Recentes</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full bg-white border rounded-lg">
                            <thead>
                                <tr class="bg-gray-100">
                                    <th class="py-2 px-4 border-b">Data</th>
                                    <th class="py-2 px-4 border-b">Galpão</th>
                                    <th class="py-2 px-4 border-b">Ovos Úteis</th>
                                    <th class="py-2 px-4 border-b">Ovos Quebrados</th>
                                    <th class="py-2 px-4 border-b">Total</th>
                                    <th class="py-2 px-4 border-b">Ações</th>
                                </tr>
                            </thead>
                            <tbody id="recentRecords">
                                <!-- Records will be inserted here by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- Dashboard Section -->
            <section id="dashboard" class="bg-white shadow-md rounded-lg p-6 mb-6 hidden">
                <h2 class="text-2xl font-bold text-primary mb-4"><i class="fas fa-chart-line mr-2"></i>Dashboard</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div class="bg-gray-100 p-4 rounded-lg">
                        <label for="dashboardDate" class="block text-gray-700 font-medium mb-2">Selecione a Data</label>
                        <input type="date" id="dashboardDate" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                    </div>
                    <div class="bg-gray-100 p-4 rounded-lg">
                        <label for="weekSelection" class="block text-gray-700 font-medium mb-2">Selecione a Semana</label>
                        <select id="weekSelection" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                            <option value="">Carregando semanas...</option>
                        </select>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div class="bg-green-50 p-6 rounded-lg shadow-sm border border-green-100">
                        <h3 class="text-lg font-semibold text-green-800 mb-2">Total de Ovos Úteis</h3>
                        <p id="totalGoodEggs" class="text-3xl font-bold text-green-600">0</p>
                    </div>
                    <div class="bg-yellow-50 p-6 rounded-lg shadow-sm border border-yellow-100">
                        <h3 class="text-lg font-semibold text-yellow-800 mb-2">Total de Ovos Quebrados</h3>
                        <p id="totalBrokenEggs" class="text-3xl font-bold text-yellow-600">0</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-lg font-semibold text-blue-800 mb-2">Total Geral</h3>
                        <p id="totalEggs" class="text-3xl font-bold text-blue-600">0</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div class="bg-white p-6 rounded-lg shadow-sm border">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">Melhor Dia de Produção</h3>
                        <div id="bestDay" class="text-gray-600">
                            <p class="text-sm">Nenhum dado disponível</p>
                        </div>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow-sm border">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">Pior Dia de Produção</h3>
                        <div id="worstDay" class="text-gray-600">
                            <p class="text-sm">Nenhum dado disponível</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-sm border mb-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Dia com Mais Ovos Quebrados</h3>
                    <div id="mostBrokenDay" class="text-gray-600">
                        <p class="text-sm">Nenhum dado disponível</p>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-sm border">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Produção Semanal</h3>
                    <div id="weeklyProduction" class="text-gray-600">
                        <p class="text-sm">Selecione uma semana para visualizar os dados</p>
                    </div>
                </div>
            </section>

            <!-- Notes Section -->
            <section id="notes" class="bg-white shadow-md rounded-lg p-6 mb-6 hidden">
                <h2 class="text-2xl font-bold text-primary mb-4"><i class="fas fa-calendar-day mr-2"></i>Anotações</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="noteDate" class="block text-gray-700 font-medium mb-2">Data da Anotação</label>
                        <input type="date" id="noteDate" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                    </div>
                    <div>
                        <label for="noteShed" class="block text-gray-700 font-medium mb-2">Galpão (Opcional)</label>
                        <input type="text" id="noteShed" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                    </div>
                </div>
                
                <div class="mt-4">
                    <label for="noteContent" class="block text-gray-700 font-medium mb-2">Anotação</label>
                    <textarea id="noteContent" rows="4" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"></textarea>
                </div>
                
                <div class="mt-4 flex justify-end space-x-4">
                    <button type="button" onclick="clearNoteForm()" class="px-6 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition">Limpar</button>
                    <button type="button" onclick="saveNote()" class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-dark transition">Salvar Anotação</button>
                </div>
                
                <div class="mt-8">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">Anotações Recentes</h3>
                    <div id="recentNotes" class="space-y-4">
                        <!-- Notes will be inserted here by JavaScript -->
                    </div>
                </div>
            </section>

            <!-- Settings Section -->
            <section id="settings" class="bg-white shadow-md rounded-lg p-6 mb-6 hidden">
                <h2 class="text-2xl font-bold text-primary mb-4"><i class="fas fa-cog mr-2"></i>Configurações</h2>
                
                <form id="settingsForm" class="space-y-6">
                    <div>
                        <label for="editFarmName" class="block text-gray-700 font-medium mb-2">Nome da Agropecuária</label>
                        <input type="text" id="editFarmName" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                    </div>
                    
                    <div>
                        <label for="editFarmSubtitle" class="block text-gray-700 font-medium mb-2">Subtítulo</label>
                        <input type="text" id="editFarmSubtitle" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                    </div>
                    
                    <div>
                        <label for="editFarmLocation" class="block text-gray-700 font-medium mb-2">Localização</label>
                        <input type="text" id="editFarmLocation" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                    </div>
                    
                    <div>
                        <label for="logoUpload" class="block text-gray-700 font-medium mb-2">Logo da Agropecuária</label>
                        <input type="file" id="logoUpload" accept="image/*" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                        <div class="mt-2">
                            <img id="settingsLogoPreview" class="logo-preview hidden" alt="Logo Preview">
                        </div>
                    </div>
                    
                    <div class="flex justify-end">
                        <button type="button" onclick="saveSettings()" class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-dark transition">Salvar Configurações</button>
                    </div>
                </form>
                
                <div class="mt-8 border-t pt-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">Exportar/Importar Dados</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="bg-gray-100 p-4 rounded-lg">
                            <h4 class="font-medium text-gray-700 mb-2">Exportar Dados</h4>
                            <button onclick="exportData()" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"><i class="fas fa-file-export mr-2"></i>Exportar Tudo</button>
                        </div>
                        <div class="bg-gray-100 p-4 rounded-lg">
                            <h4 class="font-medium text-gray-700 mb-2">Importar Dados</h4>
                            <input type="file" id="importFile" accept=".json" class="w-full mb-2">
                            <button onclick="importData()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"><i class="fas fa-file-import mr-2"></i>Importar</button>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <script>
        // Initialize data in localStorage if not exists
        function initializeData() {
            if (!localStorage.getItem('eggProductionData')) {
                const initialData = {
                    productions: [],
                    notes: [],
                    settings: {
                        farmName: "Agropecuária Família Vasconcelos",
                        farmSubtitle: "Agricultura Familiar - Sítio Sonho Meu",
                        farmLocation: "Localização: São Gonçalo do Amarante - CE",
                        logo: null
                    }
                };
                localStorage.setItem('eggProductionData', JSON.stringify(initialData));
                return initialData;
            }
            return JSON.parse(localStorage.getItem('eggProductionData'));
        }

        // Load data from localStorage
        function loadData() {
            const data = localStorage.getItem('eggProductionData');
            if (!data) {
                return initializeData();
            }
            return JSON.parse(data);
        }

        // Save data to localStorage
        function saveData(data) {
            localStorage.setItem('eggProductionData', JSON.stringify(data));
        }

        // Show selected section and hide others
        function showSection(sectionId) {
            document.querySelectorAll('main section').forEach(section => {
                section.classList.add('hidden');
            });
            document.getElementById(sectionId).classList.remove('hidden');
            
            // Load specific data when section is shown
            if (sectionId === 'dashboard') {
                loadDashboardData();
            } else if (sectionId === 'production') {
                loadRecentRecords();
            } else if (sectionId === 'notes') {
                loadRecentNotes();
            } else if (sectionId === 'settings') {
                loadSettings();
            }
        }

        // Production Form Handling
        document.getElementById('productionForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const shedName = document.getElementById('shedName').value;
            const recordDate = document.getElementById('recordDate').value;
            const goodEggs = parseInt(document.getElementById('goodEggs').value) || 0;
            const brokenEggs = parseInt(document.getElementById('brokenEggs').value) || 0;
            
            if (!shedName || !recordDate) {
                alert('Por favor, preencha todos os campos obrigatórios');
                return;
            }
            
            const data = loadData();
            const newRecord = {
                id: Date.now(),
                shedName,
                recordDate: adjustDateForStorage(recordDate), // Usando a nova função corrigida
                goodEggs,
                brokenEggs,
                total: goodEggs + brokenEggs,
                timestamp: new Date().toISOString()
            };
            
            // Ensure productions array exists
            if (!data.productions) {
                data.productions = [];
            }
            
            data.productions.push(newRecord);
            saveData(data);
            
            alert('Registro salvo com sucesso!');
            clearProductionForm();
            loadRecentRecords();
        });

        // Função corrigida para ajustar a data adicionando 1 dia
        function adjustDateForStorage(dateString) {
            const date = new Date(dateString);
            // Adiciona 1 dia para compensar o fuso horário
            date.setDate(date.getDate() + 1);
            return date.toISOString().split('T')[0];
        }

        function clearProductionForm() {
            document.getElementById('productionForm').reset();
            // Define a data atual no formato correto para o input type="date"
            const today = new Date();
            const formattedDate = today.toISOString().substr(0, 10);
            document.getElementById('recordDate').value = formattedDate;
        }

        function loadRecentRecords() {
            const data = loadData();
            const recentRecords = document.getElementById('recentRecords');
            recentRecords.innerHTML = '';
            
            if (!data.productions || data.productions.length === 0) {
                recentRecords.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-gray-500">Nenhum registro encontrado</td></tr>';
                return;
            }
            
            // Sort by date (newest first)
            const sortedProductions = [...data.productions].sort((a, b) => new Date(b.recordDate) - new Date(a.recordDate));
            
            sortedProductions.slice(0, 10).forEach(record => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50';
                row.innerHTML = `
                    <td class="py-2 px-4 border-b">${formatDate(record.recordDate)}</td>
                    <td class="py-2 px-4 border-b">${record.shedName}</td>
                    <td class="py-2 px-4 border-b">${record.goodEggs}</td>
                    <td class="py-2 px-4 border-b">${record.brokenEggs}</td>
                    <td class="py-2 px-4 border-b">${record.total}</td>
                    <td class="py-2 px-4 border-b">
                        <button onclick="editRecord(${record.id})" class="text-blue-600 hover:text-blue-800 mr-2"><i class="fas fa-edit"></i></button>
                        <button onclick="deleteRecord(${record.id})" class="text-red-600 hover:text-red-800"><i class="fas fa-trash"></i></button>
                    </td>
                `;
                recentRecords.appendChild(row);
            });
        }

        function editRecord(id) {
            const data = loadData();
            const record = data.productions.find(r => r.id === id);
            
            if (record) {
                document.getElementById('shedName').value = record.shedName;
                document.getElementById('recordDate').value = record.recordDate;
                document.getElementById('goodEggs').value = record.goodEggs;
                document.getElementById('brokenEggs').value = record.brokenEggs;
                
                // Remove the old record
                data.productions = data.productions.filter(r => r.id !== id);
                saveData(data);
                
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }

        function deleteRecord(id) {
            if (confirm('Tem certeza que deseja excluir este registro?')) {
                const data = loadData();
                data.productions = data.productions.filter(r => r.id !== id);
                saveData(data);
                loadRecentRecords();
            }
        }

        // Dashboard Functions
        function loadDashboardData() {
            const data = loadData();
            
            // Populate week selection
            const weekSelection = document.getElementById('weekSelection');
            weekSelection.innerHTML = '';
            
            if (!data.productions || data.productions.length === 0) {
                weekSelection.innerHTML = '<option value="">Nenhum dado disponível</option>';
                return;
            }
            
            // Sort productions by date
            const sortedProductions = [...data.productions].sort((a, b) => new Date(a.recordDate) - new Date(b.recordDate));
            
            // Group by weeks
            const weeks = [];
            let currentWeek = [];
            let currentWeekStart = null;
            
            sortedProductions.forEach((record, index) => {
                const recordDate = new Date(record.recordDate);
                
                if (!currentWeekStart) {
                    currentWeekStart = new Date(recordDate);
                    currentWeekStart.setHours(0, 0, 0, 0);
                    currentWeek.push(record);
                } else {
                    const daysDiff = Math.floor((recordDate - currentWeekStart) / (1000 * 60 * 60 * 24));
                    
                    if (daysDiff < 7) {
                        currentWeek.push(record);
                    } else {
                        weeks.push({
                            startDate: new Date(currentWeekStart),
                            endDate: new Date(currentWeek[currentWeek.length - 1].recordDate),
                            records: [...currentWeek]
                        });
                        
                        currentWeek = [record];
                        currentWeekStart = new Date(recordDate);
                        currentWeekStart.setHours(0, 0, 0, 0);
                    }
                }
                
                // Add the last week if we're at the end
                if (index === sortedProductions.length - 1) {
                    weeks.push({
                        startDate: new Date(currentWeekStart),
                        endDate: new Date(record.recordDate),
                        records: [...currentWeek]
                    });
                }
            });
            
            // Add week options
            weeks.forEach((week, index) => {
                const option = document.createElement('option');
                option.value = week.startDate.toISOString();
                option.textContent = `Semana ${index + 1} - ${formatDate(week.startDate)} a ${formatDate(week.endDate)}`;
                weekSelection.appendChild(option);
            });
            
            // Set default to current week if available
            if (weeks.length > 0) {
                weekSelection.value = weeks[weeks.length - 1].startDate.toISOString();
                updateWeekStats(weeks[weeks.length - 1]);
            }
            
            // Add event listeners
            document.getElementById('dashboardDate').addEventListener('change', function() {
                updateDailyStats(this.value);
            });
            
            weekSelection.addEventListener('change', function() {
                const selectedWeek = weeks.find(w => w.startDate.toISOString() === this.value);
                if (selectedWeek) {
                    updateWeekStats(selectedWeek);
                }
            });
            
            // Find best and worst days
            findBestAndWorstDays(data.productions);
        }

        function updateDailyStats(date) {
            if (!date) return;
            
            const data = loadData();
            const dailyRecords = data.productions.filter(r => r.recordDate === date);
            
            let totalGood = 0;
            let totalBroken = 0;
            let total = 0;
            
            dailyRecords.forEach(record => {
                totalGood += record.goodEggs;
                totalBroken += record.brokenEggs;
                total += record.total;
            });
            
            document.getElementById('totalGoodEggs').textContent = totalGood;
            document.getElementById('totalBrokenEggs').textContent = totalBroken;
            document.getElementById('totalEggs').textContent = total;
            
            // Update weekly production display
            document.getElementById('weeklyProduction').innerHTML = `
                <p class="mb-2">Produção em ${formatDate(date)}:</p>
                <ul class="list-disc pl-5">
                    <li>Ovos Úteis: ${totalGood}</li>
                    <li>Ovos Quebrados: ${totalBroken}</li>
                    <li>Total: ${total}</li>
                </ul>
            `;
        }

        function updateWeekStats(week) {
            let totalGood = 0;
            let totalBroken = 0;
            let total = 0;
            
            week.records.forEach(record => {
                totalGood += record.goodEggs;
                totalBroken += record.brokenEggs;
                total += record.total;
            });
            
            document.getElementById('totalGoodEggs').textContent = totalGood;
            document.getElementById('totalBrokenEggs').textContent = totalBroken;
            document.getElementById('totalEggs').textContent = total;
            
            // Update weekly production display
            document.getElementById('weeklyProduction').innerHTML = `
                <p class="mb-2">Produção na semana de ${formatDate(week.startDate)} a ${formatDate(week.endDate)}:</p>
                <ul class="list-disc pl-5">
                    <li>Ovos Úteis: ${totalGood}</li>
                    <li>Ovos Quebrados: ${totalBroken}</li>
                    <li>Total: ${total}</li>
                    <li>Média diária de ovos úteis: ${Math.round(totalGood / week.records.length)}</li>
                </ul>
            `;
        }

        function findBestAndWorstDays(productions) {
            if (!productions || productions.length === 0) return;
            
            // Group by date
            const dailyProductions = {};
            
            productions.forEach(record => {
                if (!dailyProductions[record.recordDate]) {
                    dailyProductions[record.recordDate] = {
                        goodEggs: 0,
                        brokenEggs: 0,
                        total: 0,
                        date: record.recordDate
                    };
                }
                
                dailyProductions[record.recordDate].goodEggs += record.goodEggs;
                dailyProductions[record.recordDate].brokenEggs += record.brokenEggs;
                dailyProductions[record.recordDate].total += record.total;
            });
            
            const dailyArray = Object.values(dailyProductions);
            
            // Find best day (most good eggs)
            const bestDay = dailyArray.reduce((prev, current) => 
                (prev.goodEggs > current.goodEggs) ? prev : current
            );
            
            // Find worst day (least good eggs)
            const worstDay = dailyArray.reduce((prev, current) => 
                (prev.goodEggs < current.goodEggs) ? prev : current
            );
            
            // Find day with most broken eggs
            const mostBrokenDay = dailyArray.reduce((prev, current) => 
                (prev.brokenEggs > current.brokenEggs) ? prev : current
            );
            
            // Update UI
            document.getElementById('bestDay').innerHTML = `
                <p class="font-medium">${formatDate(bestDay.date)}</p>
                <p>Ovos Úteis: ${bestDay.goodEggs}</p>
                <p>Total: ${bestDay.total}</p>
            `;
            
            document.getElementById('worstDay').innerHTML = `
                <p class="font-medium">${formatDate(worstDay.date)}</p>
                <p>Ovos Úteis: ${worstDay.goodEggs}</p>
                <p>Total: ${worstDay.total}</p>
            `;
            
            document.getElementById('mostBrokenDay').innerHTML = `
                <p class="font-medium">${formatDate(mostBrokenDay.date)}</p>
                <p>Ovos Quebrados: ${mostBrokenDay.brokenEggs}</p>
                <p>Total: ${mostBrokenDay.total}</p>
            `;
        }

        // Notes Functions
        function clearNoteForm() {
            // Define a data atual no formato correto para o input type="date"
            const today = new Date();
            const formattedDate = today.toISOString().substr(0, 10);
            document.getElementById('noteDate').value = formattedDate;
            document.getElementById('noteShed').value = '';
            document.getElementById('noteContent').value = '';
        }

        function saveNote() {
            const noteDate = document.getElementById('noteDate').value;
            const noteShed = document.getElementById('noteShed').value;
            const noteContent = document.getElementById('noteContent').value;
            
            if (!noteDate || !noteContent) {
                alert('Por favor, preencha a data e o conteúdo da anotação');
                return;
            }
            
            const data = loadData();
            const newNote = {
                id: Date.now(),
                date: adjustDateForStorage(noteDate), // Usando a mesma função corrigida
                shed: noteShed,
                content: noteContent,
                timestamp: new Date().toISOString()
            };
            
            if (!data.notes) {
                data.notes = [];
            }
            
            data.notes.push(newNote);
            saveData(data);
            
            alert('Anotação salva com sucesso!');
            clearNoteForm();
            loadRecentNotes();
        }

        function loadRecentNotes() {
            const data = loadData();
            const recentNotes = document.getElementById('recentNotes');
            recentNotes.innerHTML = '';
            
            if (!data.notes || data.notes.length === 0) {
                recentNotes.innerHTML = '<p class="text-gray-500 text-center py-4">Nenhuma anotação encontrada</p>';
                return;
            }
            
            // Sort by date (newest first)
            const sortedNotes = [...data.notes].sort((a, b) => new Date(b.date) - new Date(a.date));
            
            sortedNotes.slice(0, 10).forEach(note => {
                const noteElement = document.createElement('div');
                noteElement.className = 'bg-gray-50 p-4 rounded-lg border';
                noteElement.innerHTML = `
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-medium text-gray-800">${formatDate(note.date)}</h4>
                        <div>
                            <button onclick="editNote(${note.id})" class="text-blue-600 hover:text-blue-800 mr-2"><i class="fas fa-edit"></i></button>
                            <button onclick="deleteNote(${note.id})" class="text-red-600 hover:text-red-800"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
                    ${note.shed ? `<p class="text-sm text-gray-600 mb-2">Galpão: ${note.shed}</p>` : ''}
                    <p class="text-gray-700">${note.content}</p>
                `;
                recentNotes.appendChild(noteElement);
            });
        }

        function editNote(id) {
            const data = loadData();
            const note = data.notes.find(n => n.id === id);
            
            if (note) {
                document.getElementById('noteDate').value = note.date;
                document.getElementById('noteShed').value = note.shed || '';
                document.getElementById('noteContent').value = note.content;
                
                // Remove the old note
                data.notes = data.notes.filter(n => n.id !== id);
                saveData(data);
                
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }

        function deleteNote(id) {
            if (confirm('Tem certeza que deseja excluir esta anotação?')) {
                const data = loadData();
                data.notes = data.notes.filter(n => n.id !== id);
                saveData(data);
                loadRecentNotes();
            }
        }

        // Settings Functions
        function loadSettings() {
            const data = loadData();
            const settings = data.settings;
            
            document.getElementById('editFarmName').value = settings.farmName;
            document.getElementById('editFarmSubtitle').value = settings.farmSubtitle;
            document.getElementById('editFarmLocation').value = settings.farmLocation.replace('Localização: ', '');
            
            if (settings.logo) {
                document.getElementById('settingsLogoPreview').src = settings.logo;
                document.getElementById('settingsLogoPreview').classList.remove('hidden');
                document.getElementById('logoPreview').src = settings.logo;
                document.getElementById('logoPreview').classList.remove('hidden');
            }
        }

        function saveSettings() {
            const farmName = document.getElementById('editFarmName').value;
            const farmSubtitle = document.getElementById('editFarmSubtitle').value;
            const farmLocation = document.getElementById('editFarmLocation').value;
            
            if (!farmName || !farmSubtitle || !farmLocation) {
                alert('Por favor, preencha todos os campos');
                return;
            }
            
            const data = loadData();
            data.settings.farmName = farmName;
            data.settings.farmSubtitle = farmSubtitle;
            data.settings.farmLocation = `Localização: ${farmLocation}`;
            
            // Handle logo upload
            const logoUpload = document.getElementById('logoUpload');
            if (logoUpload.files.length > 0) {
                const file = logoUpload.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    data.settings.logo = e.target.result;
                    saveData(data);
                    
                    // Update preview
                    document.getElementById('settingsLogoPreview').src = e.target.result;
                    document.getElementById('settingsLogoPreview').classList.remove('hidden');
                    document.getElementById('logoPreview').src = e.target.result;
                    document.getElementById('logoPreview').classList.remove('hidden');
                    
                    // Update header
                    document.getElementById('farmName').textContent = farmName;
                    document.getElementById('farmSubtitle').textContent = farmSubtitle;
                    document.getElementById('farmLocation').textContent = `Localização: ${farmLocation}`;
                    
                    alert('Configurações salvas com sucesso!');
                };
                
                reader.readAsDataURL(file);
            } else {
                saveData(data);
                
                // Update header
                document.getElementById('farmName').textContent = farmName;
                document.getElementById('farmSubtitle').textContent = farmSubtitle;
                document.getElementById('farmLocation').textContent = `Localização: ${farmLocation}`;
                
                alert('Configurações salvas com sucesso!');
            }
        }

        // Data Export/Import
        function exportData() {
            const data = loadData();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `egg_production_data_${new Date().toISOString().slice(0, 10)}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        function importData() {
            const fileInput = document.getElementById('importFile');
            
            if (fileInput.files.length === 0) {
                alert('Por favor, selecione um arquivo para importar');
                return;
            }
            
            const file = fileInput.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {
                try {
                    const importedData = JSON.parse(e.target.result);
                    
                    // Basic validation
                    if (!importedData.productions || !importedData.notes || !importedData.settings) {
                        throw new Error('Formato de arquivo inválido');
                    }
                    
                    if (confirm('Isso substituirá todos os seus dados atuais. Continuar?')) {
                        localStorage.setItem('eggProductionData', JSON.stringify(importedData));
                        alert('Dados importados com sucesso!');
                        
                        // Reload all data
                        loadRecentRecords();
                        loadRecentNotes();
                        loadSettings();
                        
                        if (document.getElementById('dashboard').classList.contains('hidden') === false) {
                            loadDashboardData();
                        }
                    }
                } catch (error) {
                    alert('Erro ao importar dados: ' + error.message);
                }
            };
            
            reader.readAsText(file);
        }

        // Helper Functions
        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('pt-BR');
        }

        // Update current time
        function updateCurrentTime() {
            const now = new Date();
            const timeString = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            const dateString = now.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            
            document.getElementById('currentTime').textContent = `${dateString} - ${timeString}`;
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize data
            initializeData();
            
            // Set default date to today in production form
            const today = new Date();
            const formattedDate = today.toISOString().substr(0, 10);
            document.getElementById('recordDate').value = formattedDate;
            
            // Set default date to today in notes form
            document.getElementById('noteDate').value = formattedDate;
            
            // Load initial data
            loadRecentRecords();
            loadSettings();
            
            // Show production section by default
            showSection('production');
            
            // Update time every second
            updateCurrentTime();
            setInterval(updateCurrentTime, 1000);
            
            // Logo preview
            document.getElementById('logoUpload').addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    const file = e.target.files[0];
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        document.getElementById('settingsLogoPreview').src = e.target.result;
                        document.getElementById('settingsLogoPreview').classList.remove('hidden');
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
        });
    </script>
<p style="border-radius: 8px; text-align: center; font-size: 12px; color: #fff; margin-top: 16px;position: fixed; left: 8px; bottom: 8px; z-index: 10; background: rgba(0, 0, 0, 0.8); padding: 4px 8px;">Made with <img src="https://enzostvs-deepsite.hf.space/logo.svg" alt="DeepSite Logo" style="width: 16px; height: 16px; vertical-align: middle;display:inline-block;margin-right:3px;filter:brightness(0) invert(1);"><a href="https://enzostvs-deepsite.hf.space" style="color: #fff;text-decoration: underline;" target="_blank" >DeepSite</a> - 🧬 <a href="https://enzostvs-deepsite.hf.space?remix=ArtVasc/controle-de-produ-o" style="color: #fff;text-decoration: underline;" target="_blank" >Remix</a></p></body>
</html>

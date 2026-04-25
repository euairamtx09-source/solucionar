<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProducTech V20 | Enterprise Edition</title>
    
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        :root {
            --brand: #2563eb;
            --brand-soft: rgba(37, 99, 235, 0.1);
            --dark: #0f172a;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --bg: #f8fafc;
            --card: #ffffff;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --radius: 14px;
            --shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: var(--bg); color: var(--text-main); display: flex; min-height: 100vh; overflow: hidden; }

        /* Sidebar - Design Moderno */
        nav {
            width: 280px; background: var(--dark); color: white; padding: 2rem 1.2rem;
            display: flex; flex-direction: column; position: relative; height: 100vh;
            transition: 0.3s; z-index: 1000;
        }
        .logo-area { display: flex; align-items: center; gap: 12px; margin-bottom: 2.5rem; padding: 0 10px; }
        .logo-area i { font-size: 1.8rem; color: var(--brand); }
        .logo-area h2 { font-weight: 800; font-size: 1.3rem; letter-spacing: -0.5px; }

        nav button {
            background: none; border: none; color: #94a3b8; padding: 14px 16px; text-align: left;
            cursor: pointer; border-radius: var(--radius); margin-bottom: 8px; font-weight: 600;
            display: flex; align-items: center; gap: 14px; transition: 0.2s; font-size: 0.95rem;
        }
        nav button:hover { background: rgba(255,255,255,0.05); color: white; }
        nav button.active { background: var(--brand); color: white; box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.4); }

        /* Área Principal */
        main { flex: 1; padding: 2.5rem; overflow-y: auto; height: 100vh; }
        .section-title { margin-bottom: 2rem; }
        .section-title h1 { font-size: 1.8rem; font-weight: 800; color: var(--dark); }
        .section-title p { color: var(--text-sub); margin-top: 4px; }

        /* Cards e Layout */
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
        .card { background: var(--card); border-radius: var(--radius); padding: 1.5rem; border: 1px solid #eef2f6; box-shadow: var(--shadow); transition: 0.3s; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
        
        .stat-card { display: flex; align-items: center; gap: 1rem; }
        .stat-icon { width: 54px; height: 54px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; }

        /* Formulários Profissionais */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.25rem; align-items: end; }
        .group { display: flex; flex-direction: column; gap: 6px; }
        label { font-size: 0.75rem; font-weight: 800; color: var(--text-sub); text-transform: uppercase; letter-spacing: 0.5px; }
        input, select, textarea { 
            padding: 12px 14px; border: 2px solid #f1f5f9; border-radius: 10px; font-size: 0.95rem;
            outline: none; transition: 0.2s; background: #fff; color: var(--dark);
        }
        input:focus, select:focus { border-color: var(--brand); box-shadow: 0 0 0 4px var(--brand-soft); }

        /* Botões */
        .btn { padding: 12px 24px; border-radius: 10px; border: none; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 10px; transition: 0.2s; }
        .btn-primary { background: var(--brand); color: white; }
        .btn-success { background: var(--success); color: white; }
        .btn-danger { background: var(--danger); color: white; }
        .btn-warning { background: var(--warning); color: white; }
        .btn:active { transform: scale(0.96); }

        /* Tabelas Customizadas */
        .table-wrap { overflow-x: auto; margin-top: 1.5rem; border-radius: 12px; border: 1px solid #eef2f6; }
        table { width: 100%; border-collapse: collapse; background: white; min-width: 900px; }
        th { background: #f8fafc; padding: 16px; text-align: left; font-size: 0.75rem; font-weight: 800; color: var(--text-sub); text-transform: uppercase; border-bottom: 2px solid #f1f5f9; }
        td { padding: 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; color: var(--text-main); }
        tr:hover { background: #fafbfc; }

        /* Documento PDF e Modal */
        .modal { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.8); display: none; align-items: center; justify-content: center; z-index: 2000; padding: 20px; backdrop-filter: blur(8px); }
        .modal-content { background: white; width: 100%; max-width: 850px; border-radius: 20px; padding: 2.5rem; position: relative; max-height: 90vh; overflow-y: auto; }

        #doc-view { color: #1e293b; line-height: 1.6; }
        .doc-header { border-bottom: 3px solid var(--brand); padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
        .doc-body { margin-bottom: 30px; }
        .doc-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .doc-table th { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 12px; color: #1e293b; }
        .doc-table td { border: 1px solid #e2e8f0; padding: 12px; text-align: left; }

        /* Responsividade */
        @media (max-width: 950px) {
            body { flex-direction: column; overflow: auto; }
            nav { width: 100%; height: auto; flex-direction: row; padding: 0.8rem; overflow-x: auto; position: sticky; top: 0; }
            .logo-area, nav button span { display: none; }
            nav button { margin: 0 4px; padding: 12px; }
            main { padding: 1.5rem; height: auto; }
        }
        .hidden { display: none; }
    </style>
</head>
<body>

    <nav>
        <div class="logo-area"><i class="fas fa-microchip"></i> <h2>PRODUC<span style="color:var(--brand)">TECH</span></h2></div>
        <button onclick="tab('dash')" id="m-dash" class="active"><i class="fas fa-chart-line"></i> <span>Dashboard</span></button>
        <button onclick="tab('prod')" id="m-prod"><i class="fas fa-clipboard-list"></i> <span>Produção</span></button>
        <button onclick="tab('relat')" id="m-relat"><i class="fas fa-file-invoice-dollar"></i> <span>Relatórios</span></button>
        <button onclick="tab('func')" id="m-func"><i class="fas fa-user-tie"></i> <span>Funcionários</span></button>
        <button onclick="tab('item')" id="m-item"><i class="fas fa-box"></i> <span>Produtos</span></button>
        <button onclick="tab('serv')" id="m-serv"><i class="fas fa-screwdriver-wrench"></i> <span>Serviços</span></button>
        <button onclick="tab('cfg')" id="m-cfg"><i class="fas fa-sliders"></i> <span>Configurar</span></button>
    </nav>

    <main>
        <section id="sec-dash">
            <div class="section-title"><h1>Dashboard Executivo</h1><p>Visão geral da operação em tempo real</p></div>
            <div class="grid-stats">
                <div class="card stat-card"><div class="stat-icon" style="background:var(--brand-soft); color:var(--brand)"><i class="fas fa-cubes"></i></div><div><label>Produção Total</label><h2 id="st-qtd">0</h2></div></div>
                <div class="card stat-card"><div class="stat-icon" style="background:#dcfce7; color:var(--success)"><i class="fas fa-coins"></i></div><div><label>Faturamento</label><h2 id="st-val">R$ 0,00</h2></div></div>
                <div class="card stat-card"><div class="stat-icon" style="background:#fef3c7; color:var(--warning)"><i class="fas fa-users"></i></div><div><label>Equipe Ativa</label><h2 id="st-team">0</h2></div></div>
            </div>
            <div class="card"><canvas id="chartProd" style="max-height: 300px;"></canvas></div>
        </section>

        <section id="sec-prod" class="hidden">
            <div class="section-title"><h1>Controle de Produção</h1><p>Gerencie o fluxo diário de trabalho</p></div>
            <div class="card">
                <form id="f-prod" class="form-grid">
                    <input type="hidden" id="edit-prod-id">
                    <div class="group"><label>Data</label><input type="date" id="p-date" required></div>
                    <div class="group"><label>Colaborador</label><select id="p-func" required></select></div>
                    <div class="group"><label>Produto</label><select id="p-item" required></select></div>
                    <div class="group"><label>Serviço</label><select id="p-serv" required></select></div>
                    <div class="group"><label>Quantidade</label><input type="number" id="p-qtd" required></div>
                    <button type="submit" id="btn-prod" class="btn btn-primary"><i class="fas fa-plus"></i> Lançar</button>
                </form>
            </div>
            <div class="table-wrap card">
                <table>
                    <thead><tr><th>Data</th><th>Colaborador</th><th>Produto</th><th>Serviço</th><th>Qtd</th><th>Total</th><th>Ações</th></tr></thead>
                    <tbody id="l-prod"></tbody>
                </table>
            </div>
        </section>

        <section id="sec-relat" class="hidden">
            <div class="section-title"><h1>Relatórios de Produção</h1><p>Gere extratos profissionais por colaborador</p></div>
            <div class="grid-stats">
                <div class="card">
                    <h3 style="margin-bottom:15px">Gerar Fechamento</h3>
                    <div class="group"><label>Colaborador</label><select id="s-func"></select></div>
                    <button class="btn btn-primary" style="width:100%; margin-top:15px" onclick="openDoc()"><i class="fas fa-file-pdf"></i> Visualizar Documento</button>
                </div>
                <div class="card">
                    <h3>Performance da Equipe</h3>
                    <div id="ranking-list" style="margin-top:10px"></div>
                </div>
            </div>
        </section>

        <section id="sec-func" class="hidden">
            <div class="section-title"><h1>Equipe</h1></div>
            <div class="card"><form id="f-func" class="form-grid"><input type="hidden" id="id-func"><div class="group"><label>Nome</label><input type="text" id="fn-nome" required></div><div class="group"><label>Cargo</label><input type="text" id="fn-cargo" required></div><button type="submit" class="btn btn-primary">Salvar</button></form></div>
            <div class="table-wrap card"><table><thead><tr><th>Nome</th><th>Cargo</th><th>Ações</th></tr></thead><tbody id="l-func"></tbody></table></div>
        </section>

        <section id="sec-item" class="hidden">
            <div class="section-title"><h1>Produtos</h1></div>
            <div class="card"><form id="f-item" class="form-grid"><input type="hidden" id="id-item"><div class="group"><label>Produto</label><input type="text" id="it-nome" required></div><div class="group"><label>Descrição</label><input type="text" id="it-desc" required></div><button type="submit" class="btn btn-primary">Salvar</button></form></div>
            <div class="table-wrap card"><table><thead><tr><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead><tbody id="l-item"></tbody></table></div>
        </section>

        <section id="sec-serv" class="hidden">
            <div class="section-title"><h1>Tabela de Serviços</h1></div>
            <div class="card"><form id="f-serv" class="form-grid"><input type="hidden" id="id-serv"><div class="group"><label>Descrição</label><input type="text" id="sv-nome" required></div><div class="group"><label>Preço Unitário</label><input type="number" step="0.01" id="sv-val" required></div><button type="submit" class="btn btn-primary">Salvar</button></form></div>
            <div class="table-wrap card"><table><thead><tr><th>Serviço</th><th>Preço</th><th>Ações</th></tr></thead><tbody id="l-serv"></tbody></table></div>
        </section>

        <section id="sec-cfg" class="hidden">
            <div class="section-title"><h1>Cabeçalho Corporativo</h1><p>Dados que aparecerão nos seus documentos PDF</p></div>
            <div class="card">
                <form id="f-cfg" class="form-grid">
                    <div class="group" style="grid-column: span 2;"><label>Razão Social / Nome Fantasia</label><input type="text" id="cfg-name"></div>
                    <div class="group"><label>CNPJ / CPF</label><input type="text" id="cfg-doc"></div>
                    <div class="group"><label>Telefone</label><input type="text" id="cfg-tel"></div>
                    <div class="group" style="grid-column: span 2;"><label>Endereço / Logradouro</label><input type="text" id="cfg-end"></div>
                    <button type="submit" class="btn btn-success"><i class="fas fa-check"></i> Salvar Cabeçalho</button>
                </form>
            </div>
        </section>
    </main>

    <div class="modal" id="modal-doc">
        <div class="modal-content">
            <button onclick="closeModal()" style="position:absolute; top:20px; right:20px; border:none; background:none; font-size:1.5rem; cursor:pointer; color:var(--text-sub)">&times;</button>
            <div id="doc-render"></div>
            <div style="margin-top:30px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="generatePDF()"><i class="fas fa-download"></i> Baixar PDF</button>
                <button class="btn btn-success" onclick="window.print()"><i class="fas fa-print"></i> Imprimir</button>
                <button class="btn" style="background:#25d366; color:white" onclick="shareDoc()"><i class="fab fa-whatsapp"></i> WhatsApp</button>
            </div>
        </div>
    </div>

    <script>
        // --- NÚCLEO DE DADOS (LOCALSTORAGE) ---
        let db = {
            config: JSON.parse(localStorage.getItem('v20_cfg')) || { name: 'PRODUC TECH LTDA', doc: '00.000.000/0001-00', tel: '(11) 9999-9999', end: 'Área Industrial, 1000' },
            producao: JSON.parse(localStorage.getItem('v20_prod')) || [],
            equipe: JSON.parse(localStorage.getItem('v20_func')) || [],
            produtos: JSON.parse(localStorage.getItem('v20_item')) || [],
            servicos: JSON.parse(localStorage.getItem('v20_serv')) || []
        };

        let prodChart;

        function save() {
            Object.keys(db).forEach(k => localStorage.setItem('v20_'+k, JSON.stringify(db[k])));
            render();
        }

        function tab(name) {
            document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
            document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
            document.getElementById('sec-'+name).classList.remove('hidden');
            document.getElementById('m-'+name).classList.add('active');
            if(name === 'dash') initChart();
            render();
        }

        // --- SUBMISSÕES E EDIÇÕES ---

        // Produção
        document.getElementById('f-prod').onsubmit = function(e) {
            e.preventDefault();
            const id = document.getElementById('edit-prod-id').value;
            const func = db.equipe.find(f => f.id == document.getElementById('p-func').value);
            const item = db.produtos.find(i => i.id == document.getElementById('p-item').value);
            const serv = db.servicos.find(s => s.id == document.getElementById('p-serv').value);
            const qtd = parseFloat(document.getElementById('p-qtd').value);

            const registro = { id: id ? parseInt(id) : Date.now(), data: document.getElementById('p-date').value, funcId: func.id, funcNome: func.nome, item: item.nome, serv: serv.nome, qtd, valor: serv.val, total: qtd * serv.val };

            if(id) db.producao[db.producao.findIndex(x => x.id == id)] = registro;
            else db.producao.push(registro);
            
            this.reset(); document.getElementById('edit-prod-id').value = '';
            document.getElementById('btn-prod').innerHTML = '<i class="fas fa-plus"></i> Lançar';
            save();
        };

        function editProd(id) {
            const p = db.producao.find(x => x.id == id);
            document.getElementById('edit-prod-id').value = p.id;
            document.getElementById('p-date').value = p.data;
            document.getElementById('p-func').value = p.funcId;
            document.getElementById('p-qtd').value = p.qtd;
            document.getElementById('btn-prod').innerHTML = '<i class="fas fa-sync"></i> Atualizar';
            tab('prod');
        }

        // Funções de Cadastro Genéricas (Funcionário, Produto, Serviço)
        function register(idForm, cat, fields, editId) {
            document.getElementById(idForm).onsubmit = function(e) {
                e.preventDefault();
                const id = document.getElementById(editId).value;
                const obj = { id: id ? parseInt(id) : Date.now() };
                fields.forEach(f => obj[f.prop] = document.getElementById(f.id).value);
                if(cat === 'servicos') obj.val = parseFloat(obj.val);

                if(id) db[cat][db[cat].findIndex(x => x.id == id)] = obj;
                else db[cat].push(obj);
                this.reset(); document.getElementById(editId).value = '';
                save();
            }
        }

        register('f-func', 'equipe', [{id:'fn-nome', prop:'nome'}, {id:'fn-cargo', prop:'cargo'}], 'id-func');
        register('f-item', 'produtos', [{id:'it-nome', prop:'nome'}, {id:'it-desc', prop:'desc'}], 'id-item');
        register('f-serv', 'servicos', [{id:'sv-nome', prop:'nome'}, {id:'sv-val', prop:'val'}], 'id-serv');

        function editData(cat, id, fieldsMap, editId) {
            const x = db[cat].find(i => i.id == id);
            Object.keys(fieldsMap).forEach(k => document.getElementById(k).value = x[fieldsMap[k]]);
            document.getElementById(editId).value = x.id;
        }

        function del(cat, id) { if(confirm('Excluir permanentemente?')) { db[cat] = db[cat].filter(x => x.id !== id); save(); } }

        // --- RELATÓRIO PDF ---

        function openDoc() {
            const fId = document.getElementById('s-func').value;
            const func = db.equipe.find(f => f.id == fId);
            const records = db.producao.filter(p => p.funcId == fId);
            if(!func || records.length === 0) return alert("Sem registros para este colaborador!");

            let total = 0;
            let rows = records.map(p => {
                total += p.total;
                return `<tr><td>${p.data.split('-').reverse().join('/')}</td><td>${p.item}</td><td>${p.serv}</td><td>${p.qtd}</td><td>R$ ${p.total.toFixed(2)}</td></tr>`;
            }).join('');

            document.getElementById('doc-render').innerHTML = `
                <div id="doc-view">
                    <div class="doc-header">
                        <div>
                            <h2 style="color:var(--brand)">${db.config.name}</h2>
                            <p style="font-size:12px">${db.config.doc} | ${db.config.tel}</p>
                            <p style="font-size:12px">${db.config.end}</p>
                        </div>
                        <div style="text-align:right">
                            <h3 style="text-transform:uppercase; letter-spacing:1px">Extrato de Produção</h3>
                            <p>Emissão: ${new Date().toLocaleDateString()}</p>
                        </div>
                    </div>
                    <div class="doc-body" style="display:flex; justify-content:space-between; background:#f8fafc; padding:15px; border-radius:8px">
                        <div><label>Colaborador</label><p><b>${func.nome}</b></p></div>
                        <div><label>Cargo</label><p><b>${func.cargo}</b></p></div>
                    </div>
                    <table class="doc-table">
                        <thead><tr><th>Data</th><th>Produto</th><th>Serviço</th><th>Qtd</th><th>Subtotal</th></tr></thead>
                        <tbody>${rows}</tbody>
                    </table>
                    <div style="text-align:right; margin-top:30px">
                        <p>Total Geral Acumulado</p>
                        <h2 style="color:var(--success); font-size:28px">R$ ${total.toFixed(2)}</h2>
                    </div>
                    <div style="margin-top:60px; display:flex; justify-content:space-between">
                        <div style="border-top:1px solid #ddd; width:200px; text-align:center; padding-top:5px; font-size:10px">Visto Responsável</div>
                        <div style="border-top:1px solid #ddd; width:200px; text-align:center; padding-top:5px; font-size:10px">Assinatura Colaborador</div>
                    </div>
                </div>
            `;
            document.getElementById('modal-doc').style.display = 'flex';
        }

        function closeModal() { document.getElementById('modal-doc').style.display = 'none'; }
        function generatePDF() { const el = document.getElementById('doc-view'); html2pdf().from(el).set({ margin: 10, filename: 'Fechamento.pdf' }).save(); }
        function shareDoc() { window.open(`https://wa.me/?text=Seu relatório de produção está pronto.`); }

        // --- DASHBOARD E RENDER ---

        function initChart() {
            const ctx = document.getElementById('chartProd').getContext('2d');
            if(prodChart) prodChart.destroy();
            const last7Days = [...Array(7)].map((_, i) => {
                const d = new Date(); d.setDate(d.getDate() - i);
                return d.toISOString().split('T')[0];
            }).reverse();

            const data = last7Days.map(day => db.producao.filter(p => p.data === day).reduce((a, b) => a + b.total, 0));

            prodChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: last7Days.map(d => d.split('-').reverse().join('/')),
                    datasets: [{ label: 'Produção R$', data: data, borderColor: '#2563eb', backgroundColor: 'rgba(37, 99, 235, 0.1)', fill: true, tension: 0.4 }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }

        function render() {
            // Stats
            document.getElementById('st-qtd').innerText = db.producao.reduce((a,b)=>a+b.qtd, 0);
            document.getElementById('st-val').innerText = "R$ " + db.producao.reduce((a,b)=>a+b.total, 0).toLocaleString('pt-BR', {minimumFractionDigits: 2});
            document.getElementById('st-team').innerText = db.equipe.length;

            // Selects
            const fOpt = db.equipe.map(f => `<option value="${f.id}">${f.nome}</option>`).join('');
            document.getElementById('p-func').innerHTML = fOpt;
            document.getElementById('s-func').innerHTML = fOpt;
            document.getElementById('p-item').innerHTML = db.produtos.map(i => `<option value="${i.id}">${i.nome}</option>`).join('');
            document.getElementById('p-serv').innerHTML = db.servicos.map(s => `<option value="${s.id}">${s.nome}</option>`).join('');

            // Tabelas
            document.getElementById('l-prod').innerHTML = db.producao.map(p => `
                <tr><td>${p.data.split('-').reverse().join('/')}</td><td><b>${p.funcNome}</b></td><td>${p.item}</td><td>${p.serv}</td><td>${p.qtd}</td><td>R$ ${p.total.toFixed(2)}</td>
                <td><button class="btn-warning" style="padding:5px 8px; border-radius:6px; border:none" onclick="editProd(${p.id})"><i class="fas fa-edit"></i></button>
                <button class="btn-danger" style="padding:5px 8px; border-radius:6px; border:none" onclick="del('producao', ${p.id})"><i class="fas fa-trash"></i></button></td></tr>`).reverse().join('');

            document.getElementById('l-func').innerHTML = db.equipe.map(f => `<tr><td>${f.nome}</td><td>${f.cargo}</td><td><button class="btn-warning" style="padding:5px 8px; border:none; border-radius:6px" onclick="editData('equipe', ${f.id}, {'fn-nome':'nome', 'fn-cargo':'cargo'}, 'id-func')"><i class="fas fa-edit"></i></button> <button class="btn-danger" style="padding:5px 8px; border:none; border-radius:6px" onclick="del('equipe', ${f.id})"><i class="fas fa-trash"></i></button></td></tr>`).join('');
            document.getElementById('l-item').innerHTML = db.produtos.map(i => `<tr><td>${i.nome}</td><td>${i.desc}</td><td><button class="btn-warning" style="padding:5px 8px; border:none; border-radius:6px" onclick="editData('produtos', ${i.id}, {'it-nome':'nome', 'it-desc':'desc'}, 'id-item')"><i class="fas fa-edit"></i></button> <button class="btn-danger" style="padding:5px 8px; border:none; border-radius:6px" onclick="del('produtos', ${i.id})"><i class="fas fa-trash"></i></button></td></tr>`).join('');
            document.getElementById('l-serv').innerHTML = db.servicos.map(s => `<tr><td>${s.nome}</td><td>R$ ${s.val.toFixed(2)}</td><td><button class="btn-warning" style="padding:5px 8px; border:none; border-radius:6px" onclick="editData('servicos', ${s.id}, {'sv-nome':'nome', 'sv-val':'val'}, 'id-serv')"><i class="fas fa-edit"></i></button> <button class="btn-danger" style="padding:5px 8px; border:none; border-radius:6px" onclick="del('servicos', ${s.id})"><i class="fas fa-trash"></i></button></td></tr>`).join('');

            // Ranking
            const ranking = db.equipe.map(f => ({ nome: f.nome, total: db.producao.filter(p => p.funcId == f.id).reduce((a,b)=>a+b.total, 0) })).sort((a,b)=>b.total - a.total);
            document.getElementById('ranking-list').innerHTML = ranking.slice(0,5).map((r, i) => `<div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #f1f5f9"><span>${i+1}. ${r.nome}</span> <b>R$ ${r.total.toFixed(2)}</b></div>`).join('');
        }

        document.getElementById('f-cfg').onsubmit = function(e) {
            e.preventDefault();
            db.config = { name: document.getElementById('cfg-name').value, doc: document.getElementById('cfg-doc').value, tel: document.getElementById('cfg-tel').value, end: document.getElementById('cfg-end').value };
            save(); alert("Configurações aplicadas!");
        };

        // Inicialização
        window.onload = () => {
            document.getElementById('cfg-name').value = db.config.name;
            document.getElementById('cfg-doc').value = db.config.doc;
            document.getElementById('cfg-tel').value = db.config.tel;
            document.getElementById('cfg-end').value = db.config.end;
            document.getElementById('p-date').valueAsDate = new Date();
            tab('dash');
        };
    </script>
</body>
</html>

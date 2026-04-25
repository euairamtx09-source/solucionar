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
            --brand: #10b981; /* Verde conforme solicitado antes */
            --brand-soft: rgba(16, 185, 129, 0.1);
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

        /* Sidebar */
        nav {
            width: 280px; background: var(--dark); color: white; padding: 2rem 1.2rem;
            display: flex; flex-direction: column; position: relative; height: 100vh;
            transition: 0.3s; z-index: 1000;
        }
        .logo-area { display: flex; align-items: center; gap: 12px; margin-bottom: 2.5rem; padding: 0 10px; }
        .logo-area i { font-size: 1.8rem; color: var(--brand); }
        .logo-area h2 { font-weight: 800; font-size: 1.3rem; letter-spacing: -0.5px; color: white; }

        nav button {
            background: none; border: none; color: #94a3b8; padding: 14px 16px; text-align: left;
            cursor: pointer; border-radius: var(--radius); margin-bottom: 8px; font-weight: 600;
            display: flex; align-items: center; gap: 14px; transition: 0.2s; font-size: 0.95rem;
        }
        nav button:hover { background: rgba(255,255,255,0.05); color: white; }
        nav button.active { background: var(--brand); color: white; box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4); }

        /* Área Principal */
        main { flex: 1; padding: 2.5rem; overflow-y: auto; height: 100vh; }
        .section-title { margin-bottom: 2rem; }
        .section-title h1 { font-size: 1.8rem; font-weight: 800; color: var(--dark); }

        /* Cards */
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
        .card { background: var(--card); border-radius: var(--radius); padding: 1.5rem; border: 1px solid #eef2f6; box-shadow: var(--shadow); }
        
        .stat-card { display: flex; align-items: center; gap: 1rem; }
        .stat-icon { width: 54px; height: 54px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; }

        /* Tabelas */
        .table-wrap { overflow-x: auto; margin-top: 1.5rem; border-radius: 12px; border: 1px solid #eef2f6; background: white; }
        table { width: 100%; border-collapse: collapse; min-width: 800px; }
        th { background: #f8fafc; padding: 16px; text-align: left; font-size: 0.75rem; font-weight: 800; color: var(--text-sub); border-bottom: 2px solid #f1f5f9; }
        td { padding: 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }

        /* Forms */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; align-items: end; }
        .group { display: flex; flex-direction: column; gap: 4px; }
        label { font-size: 0.7rem; font-weight: 700; color: var(--text-sub); text-transform: uppercase; }
        input, select { padding: 10px; border-radius: 8px; border: 1px solid #ddd; outline: none; }
        
        .btn { padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; transition: 0.2s; }
        .btn-primary { background: var(--brand); color: white; }
        .btn-danger { background: var(--danger); color: white; }

        /* Modal */
        .modal { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 2000; padding: 20px; }
        .modal-content { background: white; width: 100%; max-width: 800px; border-radius: 15px; padding: 2rem; max-height: 90vh; overflow-y: auto; }

        .hidden { display: none; }
    </style>
</head>
<body>

    <nav>
        <div class="logo-area"><i class="fas fa-microchip"></i> <h2>PRODUC TECH</h2></div>
        <button onclick="tab('dash')" id="m-dash" class="active"><i class="fas fa-chart-line"></i> <span>Dashboard</span></button>
        <button onclick="tab('prod')" id="m-prod"><i class="fas fa-clipboard-list"></i> <span>Produção</span></button>
        <button onclick="tab('relat')" id="m-relat"><i class="fas fa-file-pdf"></i> <span>Relatórios</span></button>
        <button onclick="tab('func')" id="m-func"><i class="fas fa-users"></i> <span>Equipe</span></button>
        <button onclick="tab('serv')" id="m-serv"><i class="fas fa-tag"></i> <span>Preços</span></button>
    </nav>

    <main>
        <section id="sec-dash">
            <div class="section-title"><h1>Dashboard Executivo</h1></div>
            <div class="grid-stats">
                <div class="card stat-card"><div class="stat-icon" style="background:var(--brand-soft); color:var(--brand)"><i class="fas fa-box"></i></div><div><label>Qtd Total</label><h2 id="st-qtd">0</h2></div></div>
                <div class="card stat-card"><div class="stat-icon" style="background:#dcfce7; color:var(--success)"><i class="fas fa-coins"></i></div><div><label>Faturamento</label><h2 id="st-val">R$ 0,00</h2></div></div>
            </div>
            <div class="card"><canvas id="chartProd" style="max-height: 300px;"></canvas></div>
        </section>

        <section id="sec-prod" class="hidden">
            <div class="section-title"><h1>Produção Diária</h1></div>
            <div class="card">
                <form id="f-prod" class="form-grid">
                    <input type="hidden" id="edit-prod-id">
                    <div class="group"><label>Data</label><input type="date" id="p-date" required></div>
                    <div class="group"><label>Funcionário</label><select id="p-func" required></select></div>
                    <div class="group"><label>Serviço</label><select id="p-serv" required></select></div>
                    <div class="group"><label>Quantidade</label><input type="number" id="p-qtd" required></div>
                    <button type="submit" class="btn btn-primary">Lançar</button>
                </form>
            </div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>Data</th><th>Nome</th><th>Serviço</th><th>Qtd</th><th>Total</th><th>Ações</th></tr></thead>
                    <tbody id="l-prod"></tbody>
                </table>
            </div>
        </section>

        <section id="sec-relat" class="hidden">
            <div class="section-title"><h1>Gerar Extrato</h1></div>
            <div class="card" style="max-width: 400px;">
                <label>Selecionar Colaborador</label>
                <select id="s-func" style="width: 100%; margin: 10px 0;"></select>
                <button class="btn btn-primary" onclick="openDoc()" style="width: 100%;">Visualizar PDF</button>
            </div>
        </section>

        <section id="sec-func" class="hidden">
            <div class="section-title"><h1>Equipe</h1></div>
            <div class="card">
                <form id="f-func" class="form-grid">
                    <input type="hidden" id="id-func">
                    <div class="group"><label>Nome</label><input type="text" id="fn-nome" required></div>
                    <div class="group"><label>Cargo</label><input type="text" id="fn

# Seed de dados para demonstração — Projeto 3 Monitor de Eficiência Industrial OEE
# Base Exata | Dados simulados de pequena indústria em Capivari, SP

import sqlite3
import random
from datetime import date, timedelta


def seed_database(database_path):
    """Popula o banco com 8 máquinas e ~500 registros de turno dos últimos 30 dias."""
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 8 máquinas com setor e capacidade ideal por hora
    # (nome, setor, capacidade_hora)
    maquinas = [
        ('Linha 1 - Envase',        'Produção',    180),
        ('Linha 2 - Rotulagem',     'Produção',    150),
        ('Linha 3 - Pesagem',       'Produção',    120),
        ('Prensa Hidráulica A',     'Conformação',  90),
        ('Prensa Hidráulica B',     'Conformação',  90),
        ('Extrusora Principal',     'Conformação',  80),
        ('Esteira de Embalagem A',  'Embalagem',   200),
        ('Compressor Central',      'Utilidades',   60),
    ]

    cursor.executemany(
        'INSERT INTO maquinas (nome, setor, capacidade_hora) VALUES (?, ?, ?)',
        maquinas
    )
    conn.commit()

    # Busca IDs e capacidades das máquinas inseridas
    rows = cursor.execute('SELECT id, nome, capacidade_hora FROM maquinas').fetchall()
    maquinas_db = {nome: (id_, cap) for id_, nome, cap in rows}

    # Faixas de OEE por máquina
    # (disponibilidade_min, disponibilidade_max, performance_min, performance_max, qualidade_min, qualidade_max)
    faixas = {
        'Esteira de Embalagem A': (0.85, 0.99, 0.90, 1.00, 0.97, 1.00),
        'Linha 1 - Envase':       (0.85, 0.99, 0.90, 1.00, 0.97, 1.00),
        'Linha 2 - Rotulagem':    (0.85, 0.99, 0.90, 1.00, 0.97, 1.00),
        'Linha 3 - Pesagem':      (0.60, 0.90, 0.70, 0.90, 0.92, 0.98),
        'Prensa Hidráulica A':    (0.60, 0.90, 0.70, 0.90, 0.92, 0.98),
        'Extrusora Principal':    (0.60, 0.90, 0.70, 0.90, 0.92, 0.98),
        'Prensa Hidráulica B':    (0.45, 0.75, 0.55, 0.80, 0.85, 0.95),
        'Compressor Central':     (0.45, 0.75, 0.55, 0.80, 0.85, 0.95),
    }

    hoje = date.today()
    registros = []

    for nome_maquina, (id_maquina, capacidade_hora) in maquinas_db.items():
        d_min, d_max, p_min, p_max, q_min, q_max = faixas[nome_maquina]

        for dias_atras in range(30):
            data = (hoje - timedelta(days=dias_atras)).strftime('%Y-%m-%d')

            for turno in ('A', 'B', 'C'):
                # Nem toda máquina tem registro em todo turno e todo dia (~70% de cobertura)
                if random.random() > 0.70:
                    continue

                disp = random.uniform(d_min, d_max)
                perf = random.uniform(p_min, p_max)
                qual = random.uniform(q_min, q_max)

                tempo_planejado_min = 480
                tempo_operando_min = round(disp * tempo_planejado_min)
                producao_total = round(perf * capacidade_hora * (tempo_operando_min / 60))
                producao_aprovada = round(qual * producao_total)

                # Garante que aprovada nunca ultrapasse o total
                producao_aprovada = min(producao_aprovada, producao_total)

                registros.append((
                    id_maquina,
                    data,
                    turno,
                    tempo_planejado_min,
                    tempo_operando_min,
                    producao_total,
                    producao_aprovada
                ))

    cursor.executemany('''
        INSERT INTO registros_turno
            (maquina_id, data, turno, tempo_planejado_min, tempo_operando_min, producao_total, producao_aprovada)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', registros)

    conn.commit()
    conn.close()

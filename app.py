#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import mysql
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from config import Config
from models import Usuario, Analise, LogAuditoria
from datetime import datetime
import os
import re
import json
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

app = Flask(__name__)
app.config.from_object(Config)

# Configuração do MySQL
app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = Config.MYSQL_CURSORCLASS

mysql.init_app(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(user_id)

# Banco de dados de mutações (mesmo da versão anterior)
MUTACOES_DB = {
    'GBA': {'mutacoes': {
        'G2020A': {
            'doenca': 'Doença de Parkinson',
            'risco': 'Alto',
            'frequencia': '5-10% dos pacientes com Parkinson',
            'descricao': 'Mutação no gene GBA, fator de risco genético mais comum para Parkinson',
            'recomendacoes': [
                'Acompanhamento com neurologista especializado em Parkinson',
                'Avaliação genética para familiares de primeiro grau',
                'Monitoramento regular de sintomas motores e não-motores',
                'Considerar participação em ensaios clínicos para terapias GBA-alvo'
            ]
        }
    }},
    'LRRK2': {'mutacoes': {
        'G2019S': {
            'doenca': 'Doença de Parkinson',
            'risco': 'Médio-Alto',
            'frequencia': '~5% dos casos familiares',
            'descricao': 'Mutação no gene LRRK2, comum em casos familiares de Parkinson',
            'recomendacoes': [
                'Acompanhamento neurológico regular',
                'Avaliação de risco para familiares',
                'Considerar terapias neuroprotetoras'
            ]
        }
    }},
    'BRCA1': {'mutacoes': {
        '185delAG': {
            'doenca': 'Câncer de Mama e Ovário',
            'risco': 'Alto',
            'frequencia': '~1% na população Ashkenazi',
            'descricao': 'Mutação fundadora na população Ashkenazi, alto risco de câncer',
            'recomendacoes': [
                'Acompanhamento com oncogeneticista',
                'Mamografia anual a partir dos 25 anos',
                'Ressonância magnética anual de mama',
                'Considerar profilaxia cirúrgica'
            ]
        }
    }},
    'BRCA2': {'mutacoes': {
        '6174delT': {
            'doenca': 'Câncer de Mama e Ovário',
            'risco': 'Alto',
            'frequencia': '~1% na população Ashkenazi',
            'descricao': 'Mutação fundadora na população Ashkenazi',
            'recomendacoes': [
                'Acompanhamento com oncogeneticista',
                'Mamografia anual a partir dos 25 anos',
                'Ressonância magnética anual de mama',
                'Considerar profilaxia cirúrgica'
            ]
        }
    }},
    'EGFR': {'mutacoes': {
        'DEL19': {
            'doenca': 'Câncer de Pulmão de Células Não Pequenas (NSCLC)',
            'risco': 'Alto',
            'frequencia': '~45% das mutações EGFR',
            'descricao': 'Deleção no exon 19 do EGFR, sensível a inibidores de tirosina quinase',
            'recomendacoes': [
                'Avaliação oncológica imediata',
                'Teste de sensibilidade a inibidores de EGFR',
                'Considerar terapia alvo com TKIs de terceira geração'
            ]
        },
        'L858R': {
            'doenca': 'Câncer de Pulmão NSCLC',
            'risco': 'Alto',
            'frequencia': '~40% das mutações EGFR',
            'descricao': 'Mutação pontual no exon 21 do EGFR',
            'recomendacoes': [
                'Avaliação oncológica imediata',
                'Terapia alvo com inibidores de EGFR',
                'Monitoramento de resposta ao tratamento'
            ]
        }
    }},
    'KRAS': {'mutacoes': {
        'G12C': {
            'doenca': 'Câncer de Pulmão (Adenocarcinoma)',
            'risco': 'Alto',
            'frequencia': '25-30% dos adenocarcinomas de pulmão',
            'descricao': 'Mutação no codon 12 do KRAS, resistente a terapias anti-EGFR',
            'recomendacoes': [
                'Avaliação oncológica especializada',
                'Considerar terapias alvo para KRAS G12C',
                'Imunoterapia pode ser considerada'
            ]
        }
    }},
    'LMNA': {'mutacoes': {
        'R482W': {
            'doenca': 'Cardiomiopatia Dilatada',
            'risco': 'Alto',
            'frequencia': '~5% dos casos familiares',
            'descricao': 'Mutação no gene LMNA, associada a arritmias e morte súbita',
            'recomendacoes': [
                'Acompanhamento com cardiologista especializado',
                'Ecocardiograma regular (a cada 6-12 meses)',
                'Considerar implante de CDI'
            ]
        }
    }},
    'KCNQ1': {'mutacoes': {
        'A341V': {
            'doenca': 'Síndrome do QT Longo tipo 1 (LQT1)',
            'risco': 'Alto',
            'frequencia': '30-40% dos casos de LQT1',
            'descricao': 'Mutação no canal de potássio, associada a arritmias',
            'recomendacoes': [
                'Acompanhamento com cardiologista especializado',
                'ECG regular para monitoramento do intervalo QT',
                'Evitar medicamentos que prolongam o QT'
            ]
        }
    }},
    'TP53': {'mutacoes': {
        'R175H': {
            'doenca': 'Síndrome de Li-Fraumeni',
            'risco': 'Alto',
            'frequencia': 'Comum em diversos tipos de câncer',
            'descricao': 'Mutação hotspot no gene TP53, perda de função',
            'recomendacoes': [
                'Acompanhamento com oncogeneticista',
                'Programa de rastreamento para múltiplos cânceres',
                'Ressonância magnética total do corpo anual'
            ]
        }
    }}
}

# Funções de análise (mesmas da versão anterior)
def detectar_mutacoes(sequencia):
    """Detecta mutações conhecidas na sequência"""
    resultados = []
    
    padroes = {
        'GBA_G2020A': r'(GAGGGTCGGAGGGTCGGAGGG.*AGGGAGGAG)',
        'LRRK2_G2019S': r'(AGTGGCGGTGGTGGTGGT)',
        'LMNA_R482W': r'(GCCTGGCGCCGCCGCC)',
        'BRCA1_185delAG': r'(AGTCAGATCCTAGCGTCGAG)',
        'BRCA2_6174delT': r'(CTGTGTTTAGTGAGAGTTTATCAAAAGCA)',
        'EGFR_DEL19': r'(GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC)',
        'EGFR_L858R': r'(CTGACGGCCGCCGCCGCC)',
        'KRAS_G12C': r'(GCTTGTGGCGTAGGC)',
        'KCNQ1_A341V': r'(GTGGTGGCGGCGGCG)',
        'TP53_R175H': r'(CGTGTGGAGTATTTGGAT)',
        'TP53_R248Q': r'(AGGACAGCG)'
    }
    
    mapa_genes = {
        'GBA_G2020A': ('GBA', 'G2020A'),
        'LRRK2_G2019S': ('LRRK2', 'G2019S'),
        'LMNA_R482W': ('LMNA', 'R482W'),
        'BRCA1_185delAG': ('BRCA1', '185delAG'),
        'BRCA2_6174delT': ('BRCA2', '6174delT'),
        'EGFR_DEL19': ('EGFR', 'DEL19'),
        'EGFR_L858R': ('EGFR', 'L858R'),
        'KRAS_G12C': ('KRAS', 'G12C'),
        'KCNQ1_A341V': ('KCNQ1', 'A341V'),
        'TP53_R175H': ('TP53', 'R175H'),
        'TP53_R248Q': ('TP53', 'R248Q')
    }
    
    for padrao_id, regex in padroes.items():
        if re.search(regex, sequencia, re.IGNORECASE):
            gene, mutacao = mapa_genes[padrao_id]
            if gene in MUTACOES_DB and mutacao in MUTACOES_DB[gene]['mutacoes']:
                info = MUTACOES_DB[gene]['mutacoes'][mutacao]
                resultados.append({
                    'gene': gene,
                    'mutacao': mutacao,
                    'doenca': info['doenca'],
                    'risco': info['risco'],
                    'frequencia': info['frequencia'],
                    'descricao': info['descricao'],
                    'recomendacoes': info['recomendacoes']
                })
    
    return resultados

def analisar_sequencia(sequencia):
    """Análise completa da sequência"""
    a = sequencia.count('A') + sequencia.count('a')
    c = sequencia.count('C') + sequencia.count('c')
    g = sequencia.count('G') + sequencia.count('g')
    t = sequencia.count('T') + sequencia.count('t')
    total = a + c + g + t
    
    composicao = {
        'A': a, 'C': c, 'G': g, 'T': t,
        'total': total,
        'gc': round((c + g) * 100 / total, 2) if total > 0 else 0
    }
    
    mutacoes = detectar_mutacoes(sequencia)
    
    return {
        'composicao': composicao,
        'mutacoes': mutacoes,
        'tamanho': len(sequencia)
    }

def gerar_pdf(analise_id, resultado, usuario_nome):
    """Gera relatório PDF da análise"""
    filename = f"relatorios_pdf/analise_{analise_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs('relatorios_pdf', exist_ok=True)
    
    doc = SimpleDocTemplate(filename, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('CustomTitle', parent=styles['Title'], 
                                 fontSize=24, textColor=colors.darkblue)
    style_heading = ParagraphStyle('Heading', parent=styles['Heading2'],
                                   fontSize=16, textColor=colors.darkblue)
    style_normal = styles['Normal']
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontWeight='bold')
    
    story = []
    
    # Título
    story.append(Paragraph("RELATÓRIO DE ANÁLISE GENÉTICA", style_title))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", style_normal))
    story.append(Paragraph(f"Usuário: {usuario_nome}", style_normal))
    story.append(Spacer(1, 0.25*inch))
    
    # Estatísticas
    story.append(Paragraph("1. ESTATÍSTICAS DA SEQUÊNCIA", style_heading))
    story.append(Spacer(1, 0.1*inch))
    
    stats_data = [
        ['Tamanho', str(resultado['tamanho'])],
        ['Conteúdo GC', f"{resultado['composicao']['gc']}%"],
        ['Adenina (A)', str(resultado['composicao']['A'])],
        ['Citosina (C)', str(resultado['composicao']['C'])],
        ['Guanina (G)', str(resultado['composicao']['G'])],
        ['Timina (T)', str(resultado['composicao']['T'])]
    ]
    stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Mutações
    story.append(Paragraph("2. MUTAÇÕES DETECTADAS", style_heading))
    story.append(Spacer(1, 0.1*inch))
    
    if resultado['mutacoes']:
        for mut in resultado['mutacoes']:
            story.append(Paragraph(f"<b>Gene:</b> {mut['gene']} | <b>Mutação:</b> {mut['mutacao']}", style_normal))
            story.append(Paragraph(f"<b>Doença:</b> {mut['doenca']}", style_normal))
            story.append(Paragraph(f"<b>Risco:</b> {mut['risco']}", style_normal))
            story.append(Paragraph(f"<b>Frequência:</b> {mut['frequencia']}", style_normal))
            story.append(Paragraph(f"<b>Descrição:</b> {mut['descricao']}", style_normal))
            story.append(Paragraph("<b>Recomendações:</b>", style_normal))
            for rec in mut['recomendacoes']:
                story.append(Paragraph(f"• {rec}", style_normal))
            story.append(Spacer(1, 0.15*inch))
    else:
        story.append(Paragraph("✅ Nenhuma mutação patogênica detectada.", style_normal))
    
    # Rodapé
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("---", style_normal))
    story.append(Paragraph("Este relatório é para fins educacionais e de pesquisa.", style_normal))
    story.append(Paragraph("Consulte um profissional de saúde para decisões clínicas.", style_normal))
    
    doc.build(story)
    return filename

# Rotas da aplicação
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.get_by_email(email)
        if usuario and usuario.check_password(senha):
            login_user(usuario)
            usuario.update_last_login()
            LogAuditoria.log(usuario.id, 'login', f'Login realizado', request.remote_addr)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar = request.form.get('confirmar')
        
        if senha != confirmar:
            flash('As senhas não coincidem.', 'danger')
            return render_template('registro.html')
        
        if Usuario.get_by_email(email):
            flash('Este email já está cadastrado.', 'danger')
            return render_template('registro.html')
        
        try:
            Usuario.create(nome, email, senha)
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Erro ao registrar: {str(e)}', 'danger')
    
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    LogAuditoria.log(current_user.id, 'logout', 'Logout realizado', request.remote_addr)
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Contagem de análises
    total_analises = Analise.count_by_user(current_user.id)
    
    # Últimas análises
    ultimas_analises = Analise.get_by_user(current_user.id, limit=10)
    
    # Estatísticas de mutações
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) as total_mutacoes 
        FROM mutacoes_detectadas m
        JOIN analises a ON m.analise_id = a.id
        WHERE a.usuario_id = %s
    """, (current_user.id,))
    total_mutacoes = cursor.fetchone()['total_mutacoes'] if cursor.rowcount > 0 else 0
    cursor.close()
    
    return render_template('dashboard.html', 
                         total_analises=total_analises,
                         total_mutacoes=total_mutacoes,
                         ultimas_analises=ultimas_analises)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('dashboard'))
    
    if file and file.filename.endswith(('.txt', '.fasta', '.fa')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Ler o arquivo
        with open(filepath, 'r') as f:
            conteudo = f.read()
        
        # Extrair sequência
        linhas = conteudo.split('\n')
        sequencia = ''.join([linha.strip() for linha in linhas if not linha.startswith('>')])
        
        # Validar sequência
        if not re.match(r'^[ACGTacgt]+$', sequencia):
            flash('Sequência inválida. Apenas A, C, G, T são permitidos.', 'danger')
            os.remove(filepath)
            return redirect(url_for('dashboard'))
        
        # Criar análise no banco
        analise_id = Analise.create(current_user.id, sequencia, filename)
        
        # Analisar
        resultado = analisar_sequencia(sequencia)
        
        # Salvar resultados
        Analise.save_result(analise_id, resultado)
        
        # Registrar log
        LogAuditoria.log(current_user.id, 'analise', 
                        f'Análise realizada: {filename}', request.remote_addr)
        
        flash('Análise concluída com sucesso!', 'success')
        return redirect(url_for('ver_resultado', analise_id=analise_id))
    
    flash('Formato de arquivo inválido. Use .txt, .fasta ou .fa', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/resultado/<int:analise_id>')
@login_required
def ver_resultado(analise_id):
    analise = Analise.get_by_id(analise_id)
    if not analise or analise['usuario_id'] != current_user.id:
        flash('Análise não encontrada.', 'danger')
        return redirect(url_for('dashboard'))
    
    resultado = json.loads(analise['resultado_json'])
    mutacoes = Analise.get_mutacoes(analise_id)
    
    return render_template('resultado.html', 
                         analise=analise,
                         resultado=resultado,
                         mutacoes=mutacoes)

@app.route('/relatorio/<int:analise_id>')
@login_required
def ver_relatorio(analise_id):
    analise = Analise.get_by_id(analise_id)
    if not analise or analise['usuario_id'] != current_user.id:
        flash('Análise não encontrada.', 'danger')
        return redirect(url_for('dashboard'))
    
    resultado = json.loads(analise['resultado_json'])
    mutacoes = Analise.get_mutacoes(analise_id)
    
    return render_template('relatorio.html', 
                         analise=analise,
                         resultado=resultado,
                         mutacoes=mutacoes)

@app.route('/download_pdf/<int:analise_id>')
@login_required
def download_pdf(analise_id):
    analise = Analise.get_by_id(analise_id)
    if not analise or analise['usuario_id'] != current_user.id:
        flash('Análise não encontrada.', 'danger')
        return redirect(url_for('dashboard'))
    
    resultado = json.loads(analise['resultado_json'])
    
    # Gerar PDF
    pdf_path = gerar_pdf(analise_id, resultado, current_user.nome)
    
    LogAuditoria.log(current_user.id, 'download_pdf', 
                    f'Download PDF da análise {analise_id}', request.remote_addr)
    
    return send_file(pdf_path, as_attachment=True, download_name=f"relatorio_analise_{analise_id}.pdf")

@login_required
def delete_analise(analise_id):
    analise = Analise.get_by_id(analise_id)
    if not analise or analise['usuario_id'] != current_user.id:
        flash('Análise não encontrada.', 'danger')
        return redirect(url_for('historico'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM analises WHERE id = %s", (analise_id,))
    mysql.connection.commit()
    cursor.close()
    
    LogAuditoria.log(current_user.id, 'delete_analise', 
                    f'Análise {analise_id} excluída', request.remote_addr)
    
    flash('Análise excluída com sucesso.', 'success')
    return redirect(url_for('historico'))

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('resultados', exist_ok=True)
    os.makedirs('relatorios_pdf', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)

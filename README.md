# 🧬 Análise Genética Personalizada

Uma aplicação web completa para análise de mutações genéticas associadas a doenças como Parkinson, Câncer e doenças cardiovasculares.

## 📋 Sobre o Projeto

Esta aplicação permite o upload de sequências de DNA em formato FASTA ou TXT para detecção automatizada de mutações patogênicas em genes associados a doenças humanas. A ferramenta utiliza **regex** para identificação de padrões mutacionais e **BLAST local** para comparação com sequências de referência.

### 🔬 Genes Analisados

- **Parkinson**: GBA, LRRK2
- **Câncer de Mama**: BRCA1, BRCA2
- **Câncer de Pulmão**: EGFR, KRAS, TP53
- **Doenças Cardiovasculares**: LMNA, KCNQ1

### 🧬 Mutações Detectadas

| Gene | Mutação | Doença |
|------|---------|--------|
| GBA | G2020A | Parkinson |
| LRRK2 | G2019S | Parkinson |
| BRCA1 | 185delAG | Câncer de Mama/Ovário |
| BRCA2 | 6174delT | Câncer de Mama/Ovário |
| EGFR | DEL19 | Câncer de Pulmão |
| EGFR | L858R | Câncer de Pulmão |
| KRAS | G12C | Câncer de Pulmão |
| LMNA | R482W | Cardiomiopatia |
| KCNQ1 | A341V | Síndrome do QT Longo |

## 🚀 Funcionalidades

- ✅ **Autenticação de usuários** (registro/login)
- ✅ **Upload de arquivos** (.txt, .fasta, .fa)
- ✅ **Análise automática** de mutações
- ✅ **Detecção por regex** para 12 mutações
- ✅ **Dashboard** com estatísticas
- ✅ **Relatórios detalhados** em PDF
- ✅ **Download JSON** dos resultados
- ✅ **Histórico de análises**
- ✅ **Banco de dados MySQL** com logs

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Banco de Dados**: MySQL
- **Autenticação**: Flask-Login
- **Relatórios**: ReportLab (PDF)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Análise Genética**: Regex, BLAST local

## 📦 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/gersonmachado72/projeto-genetica-web.git
cd projeto-genetica-web
2. Criar ambiente virtual
bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
3. Instalar dependências
bash
pip install -r requirements.txt
4. Configurar o MySQL
bash
# Entrar no MySQL
sudo mysql -u root -p

# Executar os comandos SQL para criar o banco
# (disponíveis em database_setup.sql)
5. Configurar o arquivo config.py
python
MYSQL_USER = 'seu_usuario'
MYSQL_PASSWORD = 'sua_senha_mysql'
MYSQL_DB = 'genetica_db'
6. Executar a aplicação
bash
python app.py
Acesse: http://localhost:5000

📊 Estrutura do Projeto
text
projeto_genetica_web/
├── app.py                 # Aplicação Flask principal
├── config.py              # Configurações
├── models.py              # Modelos do banco de dados
├── database.py            # Conexão com MySQL
├── requirements.txt       # Dependências
├── templates/
│   ├── base.html         # Template base
│   ├── dashboard.html    # Dashboard do usuário
│   ├── login.html        # Login
│   ├── registro.html     # Registro
│   ├── resultado.html    # Resultados
│   └── relatorio.html    # Relatório detalhado
├── static/               # Arquivos estáticos (CSS, JS)
├── uploads/              # Arquivos enviados
├── resultados/           # Resultados JSON
└── relatorios_pdf/       # Relatórios PDF
🧪 Como Usar
Registre-se na aplicação

Faça login com seu email e senha

Faça upload de um arquivo .txt com sequência FASTA

Analise os resultados apresentados

Baixe o relatório em PDF

Acompanhe o histórico pelo Dashboard

🤝 Contribuindo
Faça um fork do projeto

Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)

Commit suas mudanças (git commit -m 'Add some AmazingFeature')

Push para a branch (git push origin feature/AmazingFeature)

Abra um Pull Request

📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

📧 Contato
Gerson Machaado - gerson72m@gmail.com

Link do Projeto: https://github.com/gersonmachado72/projeto-genetica-web.git

⚠️ Aviso
Esta ferramenta é exclusivamente para fins educacionais e de pesquisa. Não substitui diagnósticos médicos profissionais. Consulte sempre um médico geneticista para decisões clínicas.

⭐️ Se este projeto te ajudou, deixe uma estrela!

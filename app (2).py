import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

from PIL import Image as PILImage

from io import BytesIO
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Gerador de Orçamentos",
    page_icon="📄",
    layout="wide",
)

PASTA_PDFS = Path("orcamentos_gerados")
PASTA_PDFS.mkdir(exist_ok=True)

PASTA_LOGOS = Path("logos")
PASTA_LOGOS.mkdir(exist_ok=True)


# ============================================================
# DADOS DAS EMPRESAS
# ============================================================

EMPRESAS = {

    "J. MÍDIA": {
        "nome": "J. MÍDIA",
        "cnpj": "17.838.989/0001-00",
        "telefone": "(84) 99848-2455",
        "endereco": "Antonio Vitalino Reinaldo, 125 - Santa Delmira",
        "cidade": "Mossoró/RN",
        "email": "jonatanjrr@hotmail.com",
        "logo": "j_midia.png",
    },

    "MG Serviços": {
        "nome": "MG Serviços",
        "cnpj": "55.275.599/0001-68",
        "telefone": "(84) 99848 2455",
        "endereco": "Rua Maria Paiva Madruga, 101 - Santa Delmira",
        "cidade": "Mossoró/RN",
        "email": "jonatanjrr@hotmail.com",
        "logo": "mg_servicos.png",
    },
}


# ============================================================
# FORMATAÇÃO
# ============================================================

def formatar_reais(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ============================================================
# PREPARAR IMAGEM
# ============================================================

def preparar_imagem(
    arquivo,
    largura=90 * mm,
    altura=70 * mm,
):

    imagem = PILImage.open(arquivo)

    if imagem.mode != "RGB":
        imagem = imagem.convert("RGB")

    largura_px = int(largura)
    altura_px = int(altura)

    # --------------------------------------------------------
    # PROPORÇÃO DA FOTO
    # --------------------------------------------------------

    proporcao_original = (
        imagem.width / imagem.height
    )

    proporcao_destino = (
        largura_px / altura_px
    )

    # --------------------------------------------------------
    # CORTAR LATERAIS
    # --------------------------------------------------------

    if proporcao_original > proporcao_destino:

        nova_altura = imagem.height

        nova_largura = int(
            nova_altura * proporcao_destino
        )

        esquerda = (
            imagem.width - nova_largura
        ) // 2

        imagem = imagem.crop(
            (
                esquerda,
                0,
                esquerda + nova_largura,
                imagem.height,
            )
        )

    # --------------------------------------------------------
    # CORTAR PARTE DE CIMA / BAIXO
    # --------------------------------------------------------

    else:

        nova_largura = imagem.width

        nova_altura = int(
            nova_largura / proporcao_destino
        )

        topo = (
            imagem.height - nova_altura
        ) // 2

        imagem = imagem.crop(
            (
                0,
                topo,
                imagem.width,
                topo + nova_altura,
            )
        )

    # --------------------------------------------------------
    # REDIMENSIONAR
    # --------------------------------------------------------

    imagem = imagem.resize(
        (
            largura_px,
            altura_px,
        ),
        PILImage.LANCZOS,
    )

    # --------------------------------------------------------
    # BUFFER
    # --------------------------------------------------------

    buffer = BytesIO()

    imagem.save(
        buffer,
        format="JPEG",
        quality=95,
    )

    buffer.seek(0)

    return Image(
        buffer,
        width=largura,
        height=altura,
    )


# ============================================================
# ADICIONAR FOTOS
# ============================================================

def adicionar_fotos_pdf(
    elementos,
    fotos,
    titulo,
    estilo_titulo,
):

    if not fotos:
        return

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    elementos.append(
        Paragraph(
            f"<b>{titulo}</b>",
            estilo_titulo,
        )
    )

    elementos.append(
        Spacer(
            1,
            2 * mm,
        )
    )

    # --------------------------------------------------------
    # ORGANIZAR FOTOS
    # --------------------------------------------------------

    fotos_tabela = []

    linha = []

    for foto in fotos:

        imagem = preparar_imagem(
            foto,
            largura=90 * mm,
            altura=70 * mm,
        )

        linha.append(imagem)

        # Duas fotos por linha
        if len(linha) == 2:

            fotos_tabela.append(
                [
                    linha[0],
                    "",
                    linha[1],
                ]
            )

            linha = []

    # --------------------------------------------------------
    # ÚLTIMA FOTO
    # --------------------------------------------------------

    if linha:

        fotos_tabela.append(
            [
                linha[0],
                "",
                "",
            ]
        )

    # --------------------------------------------------------
    # TABELA DAS FOTOS
    # --------------------------------------------------------

    tabela_fotos = Table(
        fotos_tabela,
        colWidths=[
            90 * mm,
            5 * mm,
            90 * mm,
        ],
        splitByRow=1,
        hAlign="CENTER",
    )

    tabela_fotos.setStyle(
        TableStyle(
            [
                # Alinhamento vertical
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                # Alinhamento horizontal
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),

                # Espaçamento lateral
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),

                # Espaçamento vertical
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    elementos.append(
        tabela_fotos
    )

    elementos.append(
        Spacer(
            1,
            5 * mm,
        )
    )


# ============================================================
# TÍTULO DO SISTEMA
# ============================================================

st.title(
    "📄 Gerador de Orçamentos"
)

st.caption(
    "Crie orçamentos profissionais em PDF"
)


# ============================================================
# EMPRESA
# ============================================================

empresa_selecionada = st.selectbox(
    "Selecione a empresa",
    list(EMPRESAS.keys()),
)

dados_empresa = EMPRESAS[
    empresa_selecionada
]

empresa = dados_empresa["nome"]
cnpj = dados_empresa["cnpj"]
telefone = dados_empresa["telefone"]
endereco = dados_empresa["endereco"]
cidade = dados_empresa["cidade"]
email = dados_empresa["email"]

logo_path = (
    PASTA_LOGOS /
    dados_empresa["logo"]
)


# ============================================================
# DADOS DA EMPRESA
# ============================================================

st.markdown(
    "### 🏢 Dados da empresa"
)

col_logo, col_dados = st.columns(
    [1, 3]
)

with col_logo:

    if logo_path.exists():

        st.image(
            str(logo_path),
            width=180,
        )

    else:

        st.warning(
            f"Logo não encontrada: {logo_path}"
        )

with col_dados:

    st.markdown(
        f"""
        **{empresa}**

        **CNPJ:** {cnpj}  
        **Telefone:** {telefone}  
        **Endereço:** {endereco}  
        **Cidade:** {cidade}  
        **E-mail:** {email}
        """
    )


st.markdown("---")


# ============================================================
# DADOS DO ORÇAMENTO
# ============================================================

st.markdown(
    "### 📋 Dados do orçamento"
)

col1, col2, col3 = st.columns(3)

with col1:

    numero_orcamento = st.text_input(
        "Número do orçamento",
        value="001",
    )

with col2:

    data_orcamento = st.date_input(
        "Data do orçamento",
        value=datetime.today(),
        format="DD/MM/YYYY",
    )

with col3:

    validade = st.text_input(
        "Validade",
        value="10 dias",
    )


# ============================================================
# SOLICITANTE / CÓDIGO FISCAL
# ============================================================

col1, col2 = st.columns(2)

with col1:

    solicitante = st.text_input(
        "Solicitante",
        placeholder="Digite o nome do solicitante",
    )

with col2:

    codigo_fiscal = st.text_input(
        "Código fiscal",
        placeholder="Digite o código fiscal",
    )


# ============================================================
# SERVIÇOS
# ============================================================

st.markdown("---")

st.markdown(
    "### 🔧 Serviços / Produtos"
)


# ============================================================
# INICIALIZAR ATIVIDADES
# ============================================================

if "atividades" not in st.session_state:

    st.session_state.atividades = [
        {
            "descricao": "",
            "quantidade": 1.0,
            "valor": 0.0,
        }
    ]


# ============================================================
# FORMULÁRIO DOS SERVIÇOS
# ============================================================

for i in range(
    len(st.session_state.atividades)
):

    atividade = (
        st.session_state.atividades[i]
    )

    st.markdown(
        f"#### Serviço {i + 1}"
    )

    col1, col2, col3, col4 = st.columns(
        [4, 1.2, 1.7, 1.5]
    )

    # --------------------------------------------------------
    # DESCRIÇÃO
    # --------------------------------------------------------

    with col1:

        descricao = st.text_input(
            "Descrição do serviço / produto",
            value=atividade["descricao"],
            key=f"descricao_{i}",
            placeholder="Ex.: Pintura da fachada",
        )

        atividade["descricao"] = descricao

    # --------------------------------------------------------
    # QUANTIDADE
    # --------------------------------------------------------

    with col2:

        quantidade = st.number_input(
            "Qtd.",
            min_value=0.0,
            value=float(
                atividade["quantidade"]
            ),
            step=1.0,
            key=f"quantidade_{i}",
        )

        atividade["quantidade"] = quantidade

    # --------------------------------------------------------
    # VALOR
    # --------------------------------------------------------

    with col3:

        valor = st.number_input(
            "Valor unitário",
            min_value=0.0,
            value=float(
                atividade["valor"]
            ),
            step=10.0,
            format="%.2f",
            key=f"valor_{i}",
        )

        atividade["valor"] = valor

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total_atividade = (
        quantidade * valor
    )

    with col4:

        st.metric(
            "Total",
            formatar_reais(
                total_atividade
            ),
        )

    # --------------------------------------------------------
    # OBSERVAÇÃO
    # --------------------------------------------------------

    st.text_area(
        "Observação do serviço / produto",
        placeholder=(
            "Descreva o que será realizado "
            "ou outras informações."
        ),
        key=f"observacao_atividade_{i}",
        height=90,
    )

    # --------------------------------------------------------
    # FOTOS
    # --------------------------------------------------------

    col_antes, col_depois = st.columns(2)

    with col_antes:

        st.markdown(
            "**📷 Fotos do ANTES**"
        )

        st.file_uploader(
            "Selecione as fotos do antes",
            type=[
                "png",
                "jpg",
                "jpeg",
            ],
            accept_multiple_files=True,
            key=f"fotos_antes_{i}",
        )

    with col_depois:

        st.markdown(
            "**📷 Fotos do DEPOIS**"
        )

        st.file_uploader(
            "Selecione as fotos do depois",
            type=[
                "png",
                "jpg",
                "jpeg",
            ],
            accept_multiple_files=True,
            key=f"fotos_depois_{i}",
        )

    st.markdown("---")


# ============================================================
# ADICIONAR SERVIÇO
# ============================================================

if st.button(
    "➕ Adicionar serviço"
):

    st.session_state.atividades.append(
        {
            "descricao": "",
            "quantidade": 1.0,
            "valor": 0.0,
        }
    )

    st.rerun()


# ============================================================
# TOTAL GERAL
# ============================================================

total_geral = 0

for atividade in (
    st.session_state.atividades
):

    total_geral += (
        atividade["quantidade"]
        * atividade["valor"]
    )


st.markdown(
    f"### 💰 Total geral: "
    f"{formatar_reais(total_geral)}"
)


# ============================================================
# OBSERVAÇÕES GERAIS
# ============================================================

st.markdown(
    "### 📝 Observações gerais"
)

observacoes_gerais = st.text_area(
    "Observações gerais do orçamento",
    height=120,
    placeholder=(
        "Informações gerais do orçamento."
    ),
)


# ============================================================
# GERAR PDF
# ============================================================

st.markdown("---")

gerar_pdf = st.button(
    "📄 Gerar orçamento em PDF",
    type="primary",
)


if gerar_pdf:

    # ========================================================
    # NOME DO ARQUIVO
    # ========================================================

    nome_pdf = (
        f"Orcamento_{numero_orcamento}_"
        f"{empresa_selecionada.replace(' ', '_')}.pdf"
    )

    caminho_pdf = (
        PASTA_PDFS /
        nome_pdf
    )


    # ========================================================
    # DOCUMENTO
    # ========================================================

    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=A4,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )


    # ========================================================
    # ESTILOS
    # ========================================================

    estilos = getSampleStyleSheet()


    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Heading1"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=8,
    )


    estilo_secao = ParagraphStyle(
        "Secao",
        parent=estilos["Normal"],
        fontSize=13,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=6,
        spaceAfter=6,
    )


    # ========================================================
    # ESTILO FOTOS
    # ========================================================

    estilo_fotos = ParagraphStyle(
        "Fotos",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=18,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=1,
        spaceAfter=1,
    )


    # ========================================================
    # ESTILO SERVIÇO
    # ========================================================

    estilo_servico = ParagraphStyle(
        "Servico",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=18,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=4,
        spaceAfter=2,
    )


    estilo_descricao_relatorio = ParagraphStyle(
        "DescricaoRelatorio",
        parent=estilos["Normal"],
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=0,
        spaceAfter=6,
    )


    # ========================================================
    # ESTILO DADOS DA EMPRESA
    # ========================================================

    estilo_dados_empresa = ParagraphStyle(
        "DadosEmpresa",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=colors.black,
    )


    estilo_normal = ParagraphStyle(
        "NormalCustom",
        parent=estilos["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.black,
    )


    estilo_centro = ParagraphStyle(
        "Centro",
        parent=estilos["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.black,
    )


    estilo_direita = ParagraphStyle(
        "Direita",
        parent=estilos["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_RIGHT,
        textColor=colors.black,
    )


    # ========================================================
    # ELEMENTOS
    # ========================================================

    elementos = []


    # ========================================================
    # CABEÇALHO DA EMPRESA
    # ========================================================

    if logo_path.exists():

        logo_pdf = Image(
            str(logo_path),
            width=50 * mm,
            height=36 * mm,
        )

    else:

        logo_pdf = Paragraph(
            "LOGO",
            estilo_centro,
        )


    dados_empresa_pdf = Paragraph(
        f"""
        <b>{empresa}</b><br/>
        CNPJ: {cnpj}<br/>
        Telefone: {telefone}<br/>
        {endereco}<br/>
        {cidade}<br/>
        E-mail: {email}
        """,
        estilo_dados_empresa,
    )


    tabela_cabecalho = Table(
        [
            [
                logo_pdf,
                dados_empresa_pdf,
            ]
        ],
        colWidths=[
            60 * mm,
            115 * mm,
        ],
    )


    tabela_cabecalho.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.grey,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )


    elementos.append(
        tabela_cabecalho
    )


    elementos.append(
        Spacer(
            1,
            7 * mm,
        )
    )


    # ========================================================
    # TÍTULO
    # ========================================================

    elementos.append(
        Paragraph(
            f"ORÇAMENTO Nº {numero_orcamento}",
            estilo_titulo,
        )
    )


    # ========================================================
    # DATA E VALIDADE
    # ========================================================

    tabela_dados = Table(
        [
            [
                Paragraph(
                    f"<b>Data:</b> "
                    f"{data_orcamento.strftime('%d/%m/%Y')}",
                    estilo_normal,
                ),

                Paragraph(
                    f"<b>Validade:</b> "
                    f"{validade}",
                    estilo_normal,
                ),
            ]
        ],
        colWidths=[
            87 * mm,
            87 * mm,
        ],
    )


    tabela_dados.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.lightgrey,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )


    elementos.append(
        tabela_dados
    )


    elementos.append(
        Spacer(
            1,
            5 * mm,
        )
    )


    # ========================================================
    # SOLICITANTE / CÓDIGO FISCAL
    # ========================================================

    tabela_solicitante = Table(
        [
            [
                Paragraph(
                    f"<b>Solicitante:</b> "
                    f"{solicitante or '-'}",
                    estilo_normal,
                ),

                Paragraph(
                    f"<b>Código fiscal:</b> "
                    f"{codigo_fiscal or '-'}",
                    estilo_normal,
                ),
            ]
        ],
        colWidths=[
            87 * mm,
            87 * mm,
        ],
    )


    tabela_solicitante.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.lightgrey,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )


    elementos.append(
        tabela_solicitante
    )


    elementos.append(
        Spacer(
            1,
            7 * mm,
        )
    )


    # ========================================================
    # TABELA DOS SERVIÇOS
    # ========================================================

    tabela_atividades = []


    tabela_atividades.append(
        [
            Paragraph(
                "<b>Descrição</b>",
                estilo_centro,
            ),

            Paragraph(
                "<b>Qtd.</b>",
                estilo_centro,
            ),

            Paragraph(
                "<b>Valor unit.</b>",
                estilo_centro,
            ),

            Paragraph(
                "<b>Total</b>",
                estilo_centro,
            ),
        ]
    )


    for atividade in (
        st.session_state.atividades
    ):

        descricao = (
            atividade["descricao"]
            or "-"
        )

        quantidade = (
            atividade["quantidade"]
        )

        valor = (
            atividade["valor"]
        )

        total = (
            quantidade * valor
        )


        tabela_atividades.append(
            [
                Paragraph(
                    descricao,
                    estilo_normal,
                ),

                Paragraph(
                    f"{quantidade:g}",
                    estilo_centro,
                ),

                Paragraph(
                    formatar_reais(valor),
                    estilo_direita,
                ),

                Paragraph(
                    formatar_reais(total),
                    estilo_direita,
                ),
            ]
        )


    tabela_atividades.append(
        [
            "",
            "",
            Paragraph(
                "<b>TOTAL GERAL</b>",
                estilo_direita,
            ),
            Paragraph(
                f"<b>{formatar_reais(total_geral)}</b>",
                estilo_direita,
            ),
        ]
    )


    tabela_servicos = Table(
        tabela_atividades,
        colWidths=[
            88 * mm,
            20 * mm,
            33 * mm,
            33 * mm,
        ],
        repeatRows=1,
    )


    tabela_servicos.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.grey,
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.lightgrey,
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#EAF2F8"),
                ),

                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    colors.HexColor("#F2F2F2"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )


    elementos.append(
        tabela_servicos
    )


    # ========================================================
    # OBSERVAÇÕES GERAIS
    # ========================================================

    if observacoes_gerais.strip():

        elementos.append(
            Spacer(
                1,
                7 * mm,
            )
        )

        elementos.append(
            Paragraph(
                "OBSERVAÇÕES GERAIS",
                estilo_secao,
            )
        )

        elementos.append(
            Paragraph(
                observacoes_gerais.replace(
                    "\n",
                    "<br/>",
                ),
                estilo_normal,
            )
        )


    # ========================================================
    # VERIFICAR FOTOS
    # ========================================================

    existem_fotos = False


    for i in range(
        len(st.session_state.atividades)
    ):

        fotos_antes = (
            st.session_state.get(
                f"fotos_antes_{i}",
                [],
            )
        )

        fotos_depois = (
            st.session_state.get(
                f"fotos_depois_{i}",
                [],
            )
        )


        if fotos_antes or fotos_depois:

            existem_fotos = True
            break


    # ========================================================
    # RELATÓRIO FOTOGRÁFICO
    # ========================================================

    if existem_fotos:

        elementos.append(
            PageBreak()
        )


        elementos.append(
            Paragraph(
                "RELATÓRIO FOTOGRÁFICO",
                estilo_titulo,
            )
        )


        elementos.append(
            Spacer(
                1,
                5 * mm,
            )
        )


        # ====================================================
        # CADA SERVIÇO
        # ====================================================

        for i in range(
            len(st.session_state.atividades)
        ):

            atividade = (
                st.session_state.atividades[i]
            )


            descricao = (
                atividade["descricao"].strip()
                if atividade["descricao"]
                else ""
            )


            if not descricao:

                descricao = (
                    f"Serviço {i + 1}"
                )


            observacao = (
                st.session_state.get(
                    f"observacao_atividade_{i}",
                    "",
                )
            )


            fotos_antes = (
                st.session_state.get(
                    f"fotos_antes_{i}",
                    [],
                )
            )


            fotos_depois = (
                st.session_state.get(
                    f"fotos_depois_{i}",
                    [],
                )
            )


            # ================================================
            # SERVIÇO
            # ================================================

            elementos.append(
                Paragraph(
                    f"SERVIÇO {i + 1}",
                    estilo_servico,
                )
            )


            # ================================================
            # DESCRIÇÃO
            # ================================================

            elementos.append(
                Paragraph(
                    f"<b>Descrição:</b> {descricao}",
                    estilo_descricao_relatorio,
                )
            )


            # ================================================
            # OBSERVAÇÃO
            # ================================================

            if observacao.strip():

                observacao_formatada = (
                    observacao.replace(
                        "\n",
                        "<br/>",
                    )
                )


                elementos.append(
                    Paragraph(
                        f"<b>Observação:</b> "
                        f"{observacao_formatada}",
                        estilo_normal,
                    )
                )


                elementos.append(
                    Spacer(
                        1,
                        4 * mm,
                    )
                )


            # ================================================
            # FOTOS DO ANTES
            # ================================================

            adicionar_fotos_pdf(
                elementos,
                fotos_antes,
                "📷 FOTOS DO ANTES",
                estilo_fotos,
            )


            # ================================================
            # FOTOS DO DEPOIS
            # ================================================

            adicionar_fotos_pdf(
                elementos,
                fotos_depois,
                "📷 FOTOS DO DEPOIS",
                estilo_fotos,
            )


            elementos.append(
                Spacer(
                    1,
                    8 * mm,
                )
            )


    # ========================================================
    # GERAR PDF
    # ========================================================

    doc.build(
        elementos
    )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.success(
        "✅ Orçamento gerado com sucesso!"
    )


    with open(
        caminho_pdf,
        "rb",
    ) as arquivo_pdf:

        st.download_button(
            label="⬇️ Baixar orçamento em PDF",
            data=arquivo_pdf.read(),
            file_name=nome_pdf,
            mime="application/pdf",
        )
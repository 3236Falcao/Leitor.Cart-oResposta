import streamlit as st
import pandas as pd

# Configurações iniciais
st.set_page_config(page_title="Leitor de Cartão-Resposta", page_icon="📋", layout="wide")
st.title("📋 Leitor de Cartão-Resposta — Entrada Rápida")

NUM_QUESTOES = 22
ALTERNATIVAS = ["A", "B", "C", "D"]

# Inicialização
if "resultados" not in st.session_state:
    st.session_state["resultados"] = []

# =====================
# Seção 1: Definir Gabarito
# =====================
st.header("1️⃣ Defina o Gabarito Oficial")

gabarito_str = st.text_input(
    f"Digite o gabarito com {NUM_QUESTOES} letras (ex: ABCD...)", 
    value="A" * NUM_QUESTOES, 
    max_chars=NUM_QUESTOES
).upper()

# Validar entrada
if len(gabarito_str) != NUM_QUESTOES or any(c not in ALTERNATIVAS for c in gabarito_str):
    st.error(f"⚠️ O gabarito deve ter exatamente {NUM_QUESTOES} letras (A, B, C ou D).")
    gabarito = None
else:
    gabarito = {i+1: gabarito_str[i] for i in range(NUM_QUESTOES)}
    st.success("✅ Gabarito registrado!")

st.markdown("---")

# =====================
# Seção 2: Inserir respostas do aluno
# =====================
st.header("2️⃣ Corrigir Cartão do Aluno")

with st.form("form_aluno"):
    nome_aluno = st.text_input("Nome do aluno:")
    respostas_str = st.text_input(
        f"Respostas do aluno ({NUM_QUESTOES} letras):", 
        max_chars=NUM_QUESTOES
    ).upper()
    submitted = st.form_submit_button("📌 Corrigir")

if submitted:
    if not nome_aluno.strip():
        st.error("Digite o nome do aluno antes de corrigir.")
    elif len(respostas_str) != NUM_QUESTOES or any(c not in ALTERNATIVAS for c in respostas_str):
        st.error(f"As respostas devem ter exatamente {NUM_QUESTOES} letras (A, B, C ou D).")
    else:
        respostas = {i+1: respostas_str[i] for i in range(NUM_QUESTOES)}

        # Comparar
        acertos = sum(1 for i in range(1, NUM_QUESTOES+1) if respostas[i] == gabarito[i])
        percentual = round((acertos/NUM_QUESTOES)*100, 1)

        # Guardar
        st.session_state["resultados"].append({
            "Aluno": nome_aluno.strip(),
            "Acertos": acertos,
            "Total": NUM_QUESTOES,
            "%": percentual
        })

        # Mostrar resultado detalhado
        st.subheader(f"📑 Resultado de {nome_aluno.strip()}")
        for i in range(1, NUM_QUESTOES+1):
            correta = gabarito[i]
            resposta = respostas[i]
            if resposta == correta:
                st.markdown(f"- **Q{i}:** {resposta} ✅")
            else:
                st.markdown(f"- **Q{i}:** {resposta} ❌ (Correta: {correta})")

        st.success(f"Aluno **{nome_aluno.strip()}**: **{acertos}/{NUM_QUESTOES}** ({percentual}%).")

st.markdown("---")

# =====================
# Seção 3: Resultados da Turma
# =====================
st.header("📋 Resultados da Turma")

if st.session_state["resultados"]:
    df = pd.DataFrame(st.session_state["resultados"])
    df_sorted = df.sort_values(by="Acertos", ascending=False).reset_index(drop=True)

    st.subheader("🏆 Ranking")
    st.dataframe(df_sorted, use_container_width=True)

    media = df["Acertos"].mean()
    melhor = df["Acertos"].max()
    pior = df["Acertos"].min()
    st.info(f"📊 Estatísticas: Média = {media:.1f} | Melhor = {melhor} | Pior = {pior}")

    csv = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar resultados em CSV", data=csv, file_name="resultados_cartao_resposta.csv", mime="text/csv")

    if st.button("🗑️ Resetar Resultados da Turma"):
        st.session_state["resultados"] = []
        st.success("Resultados apagados.")
        st.rerun()
else:
    st.info("Nenhum aluno corrigido ainda.")

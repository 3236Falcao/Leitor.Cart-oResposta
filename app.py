import streamlit as st
import pandas as pd

# Configurações
st.set_page_config(page_title="Leitor de Cartão-Resposta", page_icon="📋", layout="wide")
st.title("📋 Leitor de Cartão-Resposta — Versão Estável")

NUM_QUESTOES = 22
ALTERNATIVAS = ["A", "B", "C", "D"]

# Inicialização / Flags de Reset
if "resultados" not in st.session_state:
    st.session_state["resultados"] = []

if st.session_state.get("reset_all_flag"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]

if st.session_state.get("reset_gabarito_flag"):
    for q in range(1, NUM_QUESTOES + 1):
        key = f"gabarito_{q}"
        if key in st.session_state:
            del st.session_state[key]
    if "gabarito" in st.session_state:
        del st.session_state["gabarito"]
    del st.session_state["reset_gabarito_flag"]

if st.session_state.get("reset_form_flag"):
    if "nome_aluno" in st.session_state:
        del st.session_state["nome_aluno"]
    del st.session_state["reset_form_flag"]

# Garantir chaves iniciais
for q in range(1, NUM_QUESTOES + 1):
    gkey = f"gabarito_{q}"
    if gkey not in st.session_state:
        st.session_state[gkey] = "A"

st.session_state["gabarito"] = {q: st.session_state[f"gabarito_{q}"] for q in range(1, NUM_QUESTOES + 1)}

# Controles de Reset
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🔁 Resetar Gabarito"):
        st.session_state["reset_gabarito_flag"] = True
        st.rerun()

with col2:
    if st.button("🧹 Resetar Formulário"):
        st.session_state["reset_form_flag"] = True
        st.rerun()

with col3:
    if st.button("🗑️ Resetar Sessão"):
        st.session_state["reset_all_flag"] = True
        st.rerun()

st.markdown("---")

# Seção 1: Gabarito Editável
st.header("1️⃣ Defina / Ajuste o Gabarito Oficial")
cols = st.columns(4)
for q in range(1, NUM_QUESTOES + 1):
    col = cols[(q - 1) % 4]
    with col:
        st.selectbox(f"Questão {q}", ALTERNATIVAS, key=f"gabarito_{q}", index=ALTERNATIVAS.index(st.session_state[f"gabarito_{q}"]))

st.session_state["gabarito"] = {q: st.session_state[f"gabarito_{q}"] for q in range(1, NUM_QUESTOES + 1)}

if st.button("💾 Salvar/Confirmar Gabarito"):
    st.success("Gabarito salvo na sessão.")

st.markdown("---")

# Seção 2: Formulário Manual
st.header("2️⃣ Corrigir Cartão do Aluno (entrada manual)")

with st.form(key="form_aluno"):
    nome_aluno = st.text_input("Nome do aluno:", key="nome_aluno")

    cols = st.columns(4)
    respostas_aluno = {}
    for q in range(1, NUM_QUESTOES + 1):
        col = cols[(q - 1) % 4]
        with col:
            resposta = st.selectbox(f"Q{q}", ALTERNATIVAS, key=f"resposta_{q}", index=ALTERNATIVAS.index("A"))
            respostas_aluno[q] = resposta

    submitted = st.form_submit_button("📌 Corrigir")

if submitted:
    if not nome_aluno or not nome_aluno.strip():
        st.error("Digite o nome do aluno antes de corrigir.")
    else:
        # Comparar com gabarito
        gabarito = st.session_state["gabarito"]
        acertos = sum(1 for q in range(1, NUM_QUESTOES + 1) if respostas_aluno[q] == gabarito[q])
        percentual = round((acertos / NUM_QUESTOES) * 100, 1)

        # Salvar resultado
        st.session_state["resultados"].append({
            "Aluno": nome_aluno.strip(),
            "Acertos": acertos,
            "Total": NUM_QUESTOES,
            "%": percentual
        })

        # Feedback
        st.subheader(f"📑 Resultado de {nome_aluno.strip()}")
        for q in range(1, NUM_QUESTOES + 1):
            correta = gabarito[q]
            resposta = respostas_aluno[q]
            if resposta == correta:
                st.markdown(f"- **Q{q}:** {resposta} ✅")
            else:
                st.markdown(f"- **Q{q}:** {resposta} ❌ (Correta: {correta})")

        st.success(f"Aluno **{nome_aluno.strip()}**: **{acertos}/{NUM_QUESTOES}** ({percentual}%).")

        st.session_state["reset_form_flag"] = True
        st.rerun()

st.markdown("---")

# Seção 3: Resultados da Turma
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

    st.subheader("📊 Gráfico de desempenho")
    st.bar_chart(df_sorted.set_index("Aluno")["Acertos"])

    csv = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar resultados em CSV", data=csv, file_name="resultados_cartao_resposta.csv", mime="text/csv")

    if st.button("🗑️ Resetar Resultados da Turma"):
        st.session_state["resultados"] = []
        st.success("Resultados apagados.")
        st.rerun()
else:
    st.info("Nenhum aluno corrigido ainda.")
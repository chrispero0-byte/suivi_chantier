from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Suivi de Chantier - Cameroun", page_icon="🏗️", layout="wide"
)

st.title("🏗️ Application de Suivi de Chantier & Devis (Cameroun)")
st.markdown(
    "Suivi global, gestion de la main-d'œuvre, des matériaux, du budget en FCFA"
    " et tableau récapitulatif."
)

# --- INITIALISATION DES DONNÉES (Session State) ---
if "phases" not in st.session_state:
  st.session_state.phases = pd.DataFrame({
      "Phase": [
          "1. Terrassement & Implantation",
          "2. Fouilles & Fondations",
          "3. Élévation des murs",
          "4. Coulage de la dalle",
          "5. Charpente & Toiture",
          "6. Finitions & Peinture",
      ],
      "Avancement (%)": [100, 80, 30, 0, 0, 0],
      "Statut": ["Terminé", "En cours", "En cours", "À faire", "À faire", "À faire"],
  })

if "main_d_oeuvre" not in st.session_state:
  st.session_state.main_d_oeuvre = pd.DataFrame({
      "Corps de Métier": [
          "Chef de chantier",
          "Maçon principal",
          "Manœuvres",
          "Ferrailleurs",
      ],
      "Nombre": [1, 2, 6, 2],
      "Tarif Journalier (FCFA)": [15000, 10000, 4500, 8000],
      "Jours Prévus": [60, 45, 30, 15],
  })

if "materiaux" not in st.session_state:
  st.session_state.materiaux = pd.DataFrame(columns=[
      "Matériau",
      "Quantité",
      "Date Prévue",
      "Date Effective",
      "Retard (Jours)",
      "Fournisseur",
  ])

if "journal" not in st.session_state:
  st.session_state.journal = pd.DataFrame(
      columns=["Date", "Auteur", "Avancement Global (%)", "Commentaire"]
  )

# --- BARRE LATÉRALE (Paramètres Financiers & Calendrier) ---
st.sidebar.header("Paramètres du Projet")
nom_projet = st.sidebar.text_input("Nom du Chantier", "Villa R+1 - Yaoundé")
date_debut = st.sidebar.date_input("Date de début", value=date(2026, 1, 15))
date_fin_prevue = st.sidebar.date_input(
    "Date de fin prévue", value=date(2026, 10, 15)
)

budget_total = st.sidebar.number_input(
    "Budget Prévisionnel (FCFA)", value=25000000, step=500000, format="%d"
)
budget_consomme = st.sidebar.number_input(
    "Budget Déjà Dépensé (FCFA)", value=9500000, step=250000, format="%d"
)

# Calcul avancement global
avancement_moyen = int(st.session_state.phases["Avancement (%)"].mean())

# --- SECTION 1 : TABLEAU DE BORD (KPIS) ---
st.header("📊 Tableau de Bord Global")

# Calcul sécurisé du coût de la main-d'œuvre
mo_df = st.session_state.main_d_oeuvre
cout_total_mo = (
    mo_df["Nombre"] * mo_df["Tarif Journalier (FCFA)"] * mo_df["Jours Prévus"]
).sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric(
      label="Avancement Global", value=f"{avancement_moyen}%"
  )
  st.progress(avancement_moyen / 100)

with col2:
  reste_budget = budget_total - budget_consomme
  st.metric(
      label="Budget Restant",
      value=f"{reste_budget:,.0f} FCFA".replace(",", " "),
      delta=f"{-budget_consomme / budget_total * 100:.1f}% consommés",
  )

with col3:
  st.metric(
      label="Coût Main-d'Œuvre Estimé",
      value=f"{cout_total_mo:,.0f} FCFA".replace(",", " "),
  )

with col4:
  st.metric(label="Échéance Prévue", value=str(date_fin_prevue))

st.markdown("---")

# --- SECTION 2 : FENÊTRE RÉCAPITULATIVE (Lecture seule) ---
st.header("📋 Fiche Signalétique du Chantier (Synthèse)")
st.markdown(
    "Vue d'ensemble des informations générales du projet (lecture seule) :"
)

with st.container(border=True):
  col_s1, col_s2, col_s3 = st.columns(3)
  with col_s1:
    st.markdown(f"**🏗️ Projet :** {nom_projet}")
    st.markdown(f"**💰 Budget Total :** {budget_total:,.0f} FCFA".replace(",", " "))
    st.markdown(
        f"**💸 Dépenses actuelles :** {budget_consomme:,.0f} FCFA".replace(
            ",", " "
        )
    )
  with col_s2:
    st.markdown(f"**📅 Date de Début :** {date_debut}")
    st.markdown(f"**🏁 Date de Fin Prévue :** {date_fin_prevue}")
    st.markdown(f"**📈 Avancement Actuel :** {avancement_moyen}%")
  with col_s3:
    st.markdown(
        f"**👷‍♂️ Coût Total Main-d'Œuvre :** {cout_total_mo:,.0f} FCFA".replace(
            ",", " "
        )
    )
    nb_phases_terminees = len(
        st.session_state.phases[
            st.session_state.phases["Statut"] == "Terminé"
        ]
    )
    st.markdown(
        f"**✅ Phases Terminées :** {nb_phases_terminees} /"
        f" {len(st.session_state.phases)}"
    )

st.markdown("---")

# --- SECTION 3 : GESTION DE LA MAIN-D'ŒUVRE (DEVIS) ---
st.header("👥 Gestion de la Main-d'Œuvre & Devis")
st.markdown(
    "Ajustez les effectifs, les salaires journaliers et la durée pour affiner"
    " le devis de la main-d'œuvre :"
)

edited_mo = st.data_editor(
    st.session_state.main_d_oeuvre,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_mo",
)
st.session_state.main_d_oeuvre = edited_mo

st.markdown("---")

# --- SECTION 4 : GESTION DES PHASES DU CHANTIER ---
st.header("🔨 Évolution des Phases de Construction")
edited_phases = st.data_editor(
    st.session_state.phases,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_phases",
)
st.session_state.phases = edited_phases
avancement_moyen = int(st.session_state.phases["Avancement (%)"].mean())

st.markdown("---")

# --- SECTION 5 : SUIVI DES LIVRAISONS & RETARDS ---
st.header("🚚 Suivi des Livraisons de Matériaux")

with st.form("form_materiel"):
  col_m1, col_m2, col_m3 = st.columns(3)
  with col_m1:
    materiau = st.text_input("Matériau (ex: Ciment Cimencam, Fer 12)")
    quantite = st.text_input("Quantité (ex: 150 sacs)")
  with col_m2:
    date_prevue = st.date_input(
        "Date de livraison prévue", value=date.today(), key="prev"
    )
    date_effective = st.date_input(
        "Date de livraison effective", value=date.today(), key="eff"
    )
  with col_m3:
    fournisseur = st.text_input("Fournisseur / Quincaillerie")
    submit_mat = st.form_submit_button("Enregistrer la livraison")

  if submit_mat and materiau:
    retard_jours = (date_effective - date_prevue).days
    retard_texte = (
        f"{retard_jours} jour(s) de retard"
        if retard_jours > 0
        else ("À l'heure ou en avance" if retard_jours == 0 else "En avance")
    )

    new_mat = pd.DataFrame({
        "Matériau": [materiau],
        "Quantité": [quantite],
        "Date Prévue": [str(date_prevue)],
        "Date Effective": [str(date_effective)],
        "Retard (Jours)": [retard_texte],
        "Fournisseur": [fournisseur],
    })
    st.session_state.materiaux = pd.concat(
        [st.session_state.materiaux, new_mat], ignore_index=True
    )
    st.success("Livraison enregistrée !")
    st.rerun()

if not st.session_state.materiaux.empty:
  st.dataframe(st.session_state.materiaux, use_container_width=True)
else:
  st.info("Aucune livraison enregistrée pour le moment.")

st.markdown("---")

# --- SECTION 6 : GRAPHIQUES DE PROGRESSION ---
st.header("📈 Graphiques d'Évolution")
col_g1, col_g2 = st.columns(2)

with col_g1:
  st.subheader("Progression par Phase")
  fig_bar = px.bar(
      st.session_state.phases,
      x="Avancement (%)",
      y="Phase",
      orientation="h",
      text="Avancement (%)",
      range_x=[0, 100],
      color="Statut",
      color_discrete_map={
          "Terminé": "green",
          "En cours": "orange",
          "En retard": "red",
          "À faire": "gray",
      },
  )
  fig_bar.update_layout(yaxis=dict(autorange="reversed"), height=350)
  st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
  st.subheader("Évolution Historique Pas à Pas")
  if not st.session_state.journal.empty:
    journal_sorted = st.session_state.journal.sort_values("Date")
    fig_line = px.line(
        journal_sorted,
        x="Date",
        y="Avancement Global (%)",
        markers=True,
        range_y=[0, 100],
    )
    fig_line.update_traces(line_color="#2ca02c", line_width=3)
    fig_line.update_layout(height=350)
    st.plotly_chart(fig_line, use_container_width=True)
  else:
    st.info("Remplissez le journal de chantier pour tracer la courbe.")

st.markdown("---")

# --- SECTION 7 : JOURNAL DE CHANTIER ---
st.header("📝 Journal de Chantier (Rapport Journalier)")

with st.form("form_journal"):
  col_j1, col_j2 = st.columns(2)
  with col_j1:
    date_jour = st.date_input("Date du rapport journalier", value=date.today())
  with col_j2:
    auteur = st.text_input("Rédigé par (ex: Ingénieur / Chef de chantier)")

  commentaire = st.text_area("Résumé des activités, météo, remarques...")
  submit_journal = st.form_submit_button("Valider le rapport")

  if submit_journal and commentaire:
    new_report = pd.DataFrame({
        "Date": [str(date_jour)],
        "Auteur": [auteur],
        "Avancement Global (%)": [avancement_moyen],
        "Commentaire": [commentaire],
    })
    st.session_state.journal = pd.concat(
        [st.session_state.journal, new_report], ignore_index=True
    )
    st.success("Rapport ajouté !")
    st.rerun()

if not st.session_state.journal.empty:
  st.dataframe(
      st.session_state.journal.iloc[::-1], use_container_width=True
  )
else:
  st.info("Aucun rapport journalier enregistré.")
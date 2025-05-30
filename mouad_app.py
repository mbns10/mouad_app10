import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Établissements Scolaires",
    page_icon="🏫",
    layout="wide"
)

st.title("🏫 Analyse des Établissements Scolaires - Marrakech-Asafi")
st.markdown("---")

# Sidebar pour upload du fichier
st.sidebar.title("📊 Configuration")
uploaded_file = st.sidebar.file_uploader(
    "Choisir le fichier Excel",
    type=['xlsx', 'xls'],
    help="Téléchargez votre fichier de données Excel"
)

if uploaded_file is not None:
    try:
        # Chargement des données
        df = pd.read_excel(uploaded_file)
        
        # Vérification des colonnes requises
        required_columns = ['NOM_ETABL', 'cd_com', 'CD_MIL', 'LL_MIL', 'll_com', 
                          'nefstat', 'id_eleve', 'id_classe', 'typeEtab', 
                          'libformatFr', 'LL_CYCLE']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Colonnes manquantes: {missing_columns}")
            st.stop()
        
        # Affichage des informations générales
        st.sidebar.success(f"✅ Fichier chargé avec succès!")
        st.sidebar.info(f"📊 **{len(df)}** lignes de données")
        st.sidebar.info(f"🏫 **{df['NOM_ETABL'].nunique()}** établissements uniques")
        
        # Filtrage pour Marrakech-Asafi
        if 'll_com' in df.columns:
            marrakech_asafi_keywords = ['marrakech', 'asafi', 'safi', 'marrakesh']
            marrakech_asafi_mask = df['ll_com'].str.lower().str.contains('|'.join(marrakech_asafi_keywords), na=False)
            df_filtered = df[marrakech_asafi_mask].copy()
            
            if len(df_filtered) > 0:
                st.info(f"🎯 Filtrage effectué: **{len(df_filtered)}** lignes pour Marrakech-Asafi")
            else:
                df_filtered = df.copy()
        else:
            df_filtered = df.copy()
        
        # Nettoyage et standardisation des données
        # Remplissage des valeurs manquantes
        df_filtered['LL_MIL'] = df_filtered['LL_MIL'].fillna('Non spécifié')
        df_filtered['LL_CYCLE'] = df_filtered['LL_CYCLE'].fillna('Non spécifié')
        df_filtered['libformatFr'] = df_filtered['libformatFr'].fillna('Non spécifié')
        df_filtered['NOM_ETABL'] = df_filtered['NOM_ETABL'].fillna('Non spécifié')
        df_filtered['typeEtab'] = df_filtered['typeEtab'].fillna('Non spécifié')
        df_filtered['nefstat'] = df_filtered['nefstat'].fillna('Non spécifié')
        
        # Section des filtres hiérarchiques
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Filtres Hiérarchiques")
        
        # Filtre Milieu
        milieux_disponibles = ['Tous'] + sorted(df_filtered['LL_MIL'].unique().tolist())
        milieu_selectionne = st.sidebar.selectbox("🌆 Milieu (Rural/Urbain)", milieux_disponibles)
        
        # Appliquer le filtre milieu
        if milieu_selectionne != 'Tous':
            df_filtered = df_filtered[df_filtered['LL_MIL'] == milieu_selectionne]
        
        # Filtre Commune (dépendant du milieu)
        communes_disponibles = ['Toutes'] + sorted(df_filtered['ll_com'].unique().tolist())
        commune_selectionnee = st.sidebar.selectbox("🏘️ Commune", communes_disponibles)
        
        # Appliquer le filtre commune
        if commune_selectionnee != 'Toutes':
            df_filtered = df_filtered[df_filtered['ll_com'] == commune_selectionnee]
        
        # Filtre Établissement (dépendant de la commune) - Utilisation de NOM_ETABL
        etablissements_disponibles = ['Tous'] + sorted(df_filtered['NOM_ETABL'].unique().tolist())
        etablissement_selectionne = st.sidebar.selectbox("🏫 Établissement", etablissements_disponibles)
        
        # Appliquer le filtre établissement
        if etablissement_selectionne != 'Tous':
            df_filtered = df_filtered[df_filtered['NOM_ETABL'] == etablissement_selectionne]
        
        # Filtre Cycle (hiérarchique)
        cycles_disponibles = ['Tous'] + sorted(df_filtered['LL_CYCLE'].unique().tolist())
        cycle_selectionne = st.sidebar.selectbox("🎓 Cycle", cycles_disponibles)
        
        # Appliquer le filtre cycle
        if cycle_selectionne != 'Tous':
            df_filtered = df_filtered[df_filtered['LL_CYCLE'] == cycle_selectionne]
        
        # Filtre Niveau (dépendant du cycle)
        niveaux_disponibles = ['Tous'] + sorted(df_filtered['libformatFr'].unique().tolist())
        niveau_selectionne = st.sidebar.selectbox("📚 Niveau", niveaux_disponibles)
        
        # Appliquer le filtre niveau
        if niveau_selectionne != 'Tous':
            df_filtered = df_filtered[df_filtered['libformatFr'] == niveau_selectionne]
        
        # Affichage des données filtrées
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Données Filtrées")
        st.sidebar.info(f"📊 **{len(df_filtered)}** lignes")
        st.sidebar.info(f"🏫 **{df_filtered['NOM_ETABL'].nunique()}** établissements")
        st.sidebar.info(f"👥 **{df_filtered['id_eleve'].nunique()}** élèves")
        
        # Onglets principaux
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Vue d'ensemble", 
            "🏫 Analyse Établissements", 
            "👥 Analyse Élèves", 
            "📍 Analyse Provinciale",
            "📈 Visualisations Personnalisées"
        ])
        
        with tab1:
            st.header("📊 Vue d'ensemble des données")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🏫 Établissements", df_filtered['NOM_ETABL'].nunique())
            
            with col2:
                st.metric("👥 Élèves", df_filtered['id_eleve'].nunique())
            
            with col3:
                st.metric("🏛️ Classes", df_filtered['id_classe'].nunique())
            
            with col4:
                st.metric("🏛️ Types d'Établ.", df_filtered['libformatFr'].nunique())
            
            # Répartition urbain/rural
            st.subheader("🌆 Répartition Urbain/Rural")
            
            # Calculer les nombres uniques d'établissements par milieu
            etab_par_milieu = df_filtered.groupby('LL_MIL')['NOM_ETABL'].nunique()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    values=etab_par_milieu.values,
                    names=etab_par_milieu.index,
                    title="Répartition des établissements par milieu",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Préparer les statistiques
                milieu_stats = df_filtered.groupby('LL_MIL').agg({
                    'NOM_ETABL': 'nunique',
                    'id_eleve': 'nunique'
                }).rename(columns={'NOM_ETABL': 'Établissements', 'id_eleve': 'Élèves'})
                
                st.dataframe(milieu_stats)
            
            # Répartition par type d'établissement
            st.subheader("🏛️ Répartition par Type d'Établissement")
            
            type_stats = df_filtered.groupby('libformatFr').agg({
                'NOM_ETABL': 'nunique',
                'id_eleve': 'nunique'
            }).rename(columns={'NOM_ETABL': 'Établissements', 'id_eleve': 'Élèves'})
            
            fig_type = px.bar(
                x=type_stats.index,
                y=type_stats['Établissements'],
                title="Nombre d'établissements par type",
                labels={'x': 'Type d\'Établissement', 'y': 'Nombre d\'Établissements'}
            )
            st.plotly_chart(fig_type, use_container_width=True)
            
            # Répartition par cycle
            st.subheader("🎓 Répartition par Cycle")
            
            cycle_stats = df_filtered.groupby('LL_CYCLE').agg({
                'NOM_ETABL': 'nunique',
                'id_eleve': 'nunique'
            }).rename(columns={'NOM_ETABL': 'Établissements', 'id_eleve': 'Élèves'})
            
            fig_cycle = px.bar(
                x=cycle_stats.index,
                y=cycle_stats['Élèves'],
                title="Nombre d'élèves par cycle",
                labels={'x': 'Cycle', 'y': 'Nombre d\'élèves'}
            )
            st.plotly_chart(fig_cycle, use_container_width=True)
            st.dataframe(cycle_stats)
        
        with tab2:
            st.header("🏫 Analyse des Établissements")
            
            # Analyse du nombre de classes par établissement
            st.subheader("📚 Nombre de classes par établissement")
            
            classes_par_etab = df_filtered.groupby(['NOM_ETABL', 'LL_MIL'])['id_classe'].nunique().reset_index()
            classes_par_etab.columns = ['Nom_Etablissement', 'Milieu', 'Nombre_Classes']
            
            fig_classes = px.bar(
                classes_par_etab,
                x='Nom_Etablissement',
                y='Nombre_Classes',
                color='Milieu',
                hover_data=[],
                title="Nombre de classes par établissement et milieu",
                labels={'Nom_Etablissement': 'Nom Établissement', 'Nombre_Classes': 'Nombre de Classes'}
            )
            fig_classes.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_classes, use_container_width=True)
            
            # Statistiques détaillées par établissement
            st.subheader("📊 Statistiques détaillées par établissement")
            
            stats_etablissement = df_filtered.groupby(['NOM_ETABL', 'LL_MIL', 'll_com']).agg({
                'id_classe': 'nunique',
                'id_eleve': 'nunique'
            }).reset_index()
            
            stats_etablissement.columns = ['Nom Établissement', 'Milieu', 'Commune', 'Classes', 'Élèves']
            st.dataframe(stats_etablissement, use_container_width=True)
            
            # Analyse par type d'établissement
            st.subheader("🏛️ Analyse par type d'établissement")
            
            type_analysis = df_filtered.groupby(['libformatFr', 'LL_MIL']).agg({
                'NOM_ETABL': 'nunique',
                'id_eleve': 'nunique',
                'id_classe': 'nunique'
            }).reset_index()
            
            type_analysis.columns = ['Type', 'Milieu', 'Établissements', 'Élèves', 'Classes']
            
            fig_type_milieu = px.bar(
                type_analysis,
                x='Type',
                y='Établissements',
                color='Milieu',
                title="Nombre d'établissements par type et milieu",
                labels={'Type': 'Type d\'Établissement', 'Établissements': 'Nombre d\'Établissements'}
            )
            fig_type_milieu.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_type_milieu, use_container_width=True)
            
            st.dataframe(type_analysis, use_container_width=True)
        
        with tab3:
            st.header("👥 Analyse des Élèves")
            
            # Analyse par niveau détaillé
            st.subheader("📚 Répartition des élèves par niveau")
            
            niveau_stats = df_filtered.groupby(['LL_CYCLE', 'libformatFr']).agg({
                'id_eleve': 'nunique'
            }).reset_index()
            niveau_stats.columns = ['Cycle', 'Niveau', 'Nombre_Eleves']
            
            # Graphique par cycle et niveau
            fig_niveau = px.bar(
                niveau_stats,
                x='Niveau',
                y='Nombre_Eleves',
                color='Cycle',
                title="Nombre d'élèves par niveau et cycle",
                labels={'Niveau': 'Niveau', 'Nombre_Eleves': 'Nombre d\'élèves'}
            )
            fig_niveau.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_niveau, use_container_width=True)
            
            # Tableau détaillé
            st.dataframe(niveau_stats, use_container_width=True)
            
            # Analyse des élèves par type d'établissement
            st.subheader("🏛️ Répartition des élèves par type d'établissement")
            
            eleves_par_type = df_filtered.groupby(['libformatFr', 'LL_CYCLE']).agg({
                'id_eleve': 'nunique'
            }).reset_index()
            eleves_par_type.columns = ['Type_Etablissement', 'Cycle', 'Nombre_Eleves']
            
            fig_eleves_type = px.bar(
                eleves_par_type,
                x='Type_Etablissement',
                y='Nombre_Eleves',
                color='Cycle',
                title="Nombre d'élèves par type d'établissement et cycle",
                labels={'Type_Etablissement': 'Type d\'Établissement', 'Nombre_Eleves': 'Nombre d\'élèves'}
            )
            fig_eleves_type.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_eleves_type, use_container_width=True)
            
            st.dataframe(eleves_par_type, use_container_width=True)
        
        with tab4:
            st.header("📍 Analyse Provinciale")
            
            # Statistiques par province
            st.subheader("🏛️ Statistiques par province")
            
            stats_province = df_filtered.groupby('ll_com').agg({
                'NOM_ETABL': 'nunique',
                'id_eleve': 'nunique'
            }).reset_index()
            
            stats_province.columns = ['Province', 'Établissements', 'Élèves']
            stats_province = stats_province.sort_values('Établissements', ascending=False)
            
            st.dataframe(stats_province, use_container_width=True)
            
            # Répartition urbain/rural par province
            st.subheader("🌆 Répartition urbain/rural par province")
            
            province_milieu = df_filtered.groupby(['ll_com', 'LL_MIL']).agg({
                'NOM_ETABL': 'nunique',
                'id_eleve': 'nunique'
            }).reset_index()
            
            province_milieu.columns = ['Province', 'Milieu', 'Établissements', 'Élèves']
            
            # Visualisation par province et milieu
            fig_province = px.bar(
                province_milieu,
                x='Province',
                y='Établissements',
                color='Milieu',
                title="Nombre d'établissements par province et milieu",
                labels={'Province': 'Province', 'Établissements': 'Nombre d\'Établissements'}
            )
            fig_province.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_province, use_container_width=True)
            
            # Tableau détaillé
            st.subheader("📊 Tableau détaillé par province et milieu")
            st.dataframe(province_milieu, use_container_width=True)
        
        with tab5:
            st.header("📈 Visualisations Personnalisées")
            
            # Définition des colonnes catégorielles
            categorical_columns = df_filtered.select_dtypes(exclude=[np.number]).columns.tolist()
            
            # Section des statistiques descriptives
            st.subheader("📊 Statistiques Descriptives")

            # Sélection des colonnes numériques pour les statistiques
            numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()

            if len(numeric_cols) > 0:
                col_stats, col_groupby = st.columns(2)
                
                with col_stats:
                    selected_numeric_col = st.selectbox(
                        "Choisir une colonne numérique pour les statistiques",
                        numeric_cols,
                        help="Sélectionnez une colonne numérique pour afficher les statistiques descriptives"
                    )
                
                with col_groupby:
                    groupby_options = [None] + categorical_columns
                    groupby_col = st.selectbox(
                        "Grouper par (optionnel)",
                        groupby_options,
                        help="Optionnel: Grouper les statistiques par une colonne catégorielle"
                    )
                
                if st.button("📈 Calculer les statistiques"):
                    try:
                        if groupby_col is None:
                            # Statistiques globales
                            stats_data = {
                                'Statistique': ['Nombre de valeurs', 'Moyenne', 'Médiane', 'Écart-type', 
                                                'Minimum', 'Maximum', '1er Quartile (Q1)', '3ème Quartile (Q3)'],
                                'Valeur': [
                                    df_filtered[selected_numeric_col].count(),
                                    round(df_filtered[selected_numeric_col].mean(), 2),
                                    round(df_filtered[selected_numeric_col].median(), 2),
                                    round(df_filtered[selected_numeric_col].std(), 2),
                                    df_filtered[selected_numeric_col].min(),
                                    df_filtered[selected_numeric_col].max(),
                                    round(df_filtered[selected_numeric_col].quantile(0.25), 2),
                                    round(df_filtered[selected_numeric_col].quantile(0.75), 2)
                                ]
                            }
                            
                            stats_df = pd.DataFrame(stats_data)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Statistiques pour: {selected_numeric_col}**")
                                st.dataframe(stats_df, use_container_width=True)
                            
                            with col2:
                                # Graphique de distribution
                                fig_hist = px.histogram(
                                    df_filtered, 
                                    x=selected_numeric_col,
                                    title=f"Distribution de {selected_numeric_col}",
                                    nbins=20
                                )
                                st.plotly_chart(fig_hist, use_container_width=True)
                            
                            # Box plot pour visualiser les quartiles
                            fig_box = px.box(
                                df_filtered,
                                y=selected_numeric_col,
                                title=f"Box Plot - {selected_numeric_col}"
                            )
                            st.plotly_chart(fig_box, use_container_width=True)
                            
                        else:
                            # Statistiques groupées
                            grouped_stats = df_filtered.groupby(groupby_col)[selected_numeric_col].agg([
                                'count', 'mean', 'median', 'std', 'min', 'max',
                                lambda x: x.quantile(0.25),  # Q1
                                lambda x: x.quantile(0.75)   # Q3
                            ]).round(2)
                            
                            grouped_stats.columns = ['Nombre', 'Moyenne', 'Médiane', 'Écart-type', 
                                                    'Minimum', 'Maximum', 'Q1', 'Q3']
                            
                            st.write(f"**Statistiques de {selected_numeric_col} par {groupby_col}**")
                            st.dataframe(grouped_stats, use_container_width=True)
                            
                            # Graphiques comparatifs
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Box plot groupé
                                fig_box_grouped = px.box(
                                    df_filtered,
                                    x=groupby_col,
                                    y=selected_numeric_col,
                                    title=f"Box Plot - {selected_numeric_col} par {groupby_col}"
                                )
                                fig_box_grouped.update_layout(xaxis_tickangle=-45)
                                st.plotly_chart(fig_box_grouped, use_container_width=True)
                            
                            with col2:
                                # Graphique des moyennes
                                means_data = df_filtered.groupby(groupby_col)[selected_numeric_col].mean().reset_index()
                                fig_means = px.bar(
                                    means_data,
                                    x=groupby_col,
                                    y=selected_numeric_col,
                                    title=f"Moyenne de {selected_numeric_col} par {groupby_col}"
                                )
                                fig_means.update_layout(xaxis_tickangle=-45)
                                st.plotly_chart(fig_means, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"Erreur lors du calcul des statistiques: {str(e)}")

            else:
                st.info("Aucune colonne numérique disponible pour les statistiques descriptives.")

            # Séparateur avant la section suivante
            st.markdown("---")

            st.subheader("🎛️ Créer votre propre visualisation")
            
            st.subheader("🎛️ Créer votre propre visualisation")
            
            # Sélection des colonnes numériques et catégorielles
            numeric_columns = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = df_filtered.select_dtypes(exclude=[np.number]).columns.tolist()
            all_columns = df_filtered.columns.tolist()
            
            col1, col2 = st.columns(2)
            
            with col1:
                x_axis = st.selectbox("Choisir l'axe X", all_columns, index=0)
                chart_type = st.selectbox("Type de graphique", 
                                        ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram"])
            
            with col2:
                y_axis = st.selectbox("Choisir l'axe Y", all_columns, index=1 if len(all_columns) > 1 else 0)
                color_by = st.selectbox("Colorer par", [None] + categorical_columns)
            
            if st.button("🎨 Générer le graphique"):
                try:
                    if chart_type == "Bar Chart":
                        if df_filtered[x_axis].dtype == 'object':
                            chart_data = df_filtered.groupby(x_axis)[y_axis].count().reset_index()
                            fig = px.bar(chart_data, x=x_axis, y=y_axis, 
                                       title=f"Bar Chart: {y_axis} par {x_axis}")
                        else:
                            fig = px.bar(df_filtered, x=x_axis, y=y_axis, color=color_by,
                                       title=f"Bar Chart: {y_axis} vs {x_axis}")
                    
                    elif chart_type == "Line Chart":
                        fig = px.line(df_filtered, x=x_axis, y=y_axis, color=color_by,
                                    title=f"Line Chart: {y_axis} vs {x_axis}")
                    
                    elif chart_type == "Scatter Plot":
                        fig = px.scatter(df_filtered, x=x_axis, y=y_axis, color=color_by,
                                       title=f"Scatter Plot: {y_axis} vs {x_axis}")
                    
                    elif chart_type == "Box Plot":
                        fig = px.box(df_filtered, x=x_axis, y=y_axis, color=color_by,
                                   title=f"Box Plot: {y_axis} par {x_axis}")
                    
                    elif chart_type == "Histogram":
                        fig = px.histogram(df_filtered, x=x_axis, color=color_by,
                                         title=f"Histogram: {x_axis}")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la création du graphique: {str(e)}")
        
        # Section de renommage des colonnes
        st.sidebar.markdown("---")
        st.sidebar.subheader("✏️ Renommer les Colonnes")
        
        if st.sidebar.button("🔧 Ouvrir l'éditeur de colonnes"):
            st.subheader("✏️ Renommer les Colonnes")
            
            # Créer un formulaire pour renommer les colonnes
            with st.form("rename_columns_form"):
                st.write("Renommez les colonnes selon vos besoins :")
                
                new_column_names = {}
                for col in df_filtered.columns:
                    new_name = st.text_input(f"Renommer '{col}':", value=col)
                    if new_name != col:
                        new_column_names[col] = new_name
                
                submitted = st.form_submit_button("💾 Appliquer les changements")
                
                if submitted and new_column_names:
                    df_filtered = df_filtered.rename(columns=new_column_names)
                    st.success(f"✅ Colonnes renommées: {list(new_column_names.values())}")
                    st.experimental_rerun()
        
        # Section de téléchargement des résultats
        st.sidebar.markdown("---")
        st.sidebar.subheader("💾 Télécharger les résultats")
        
        if st.sidebar.button("📊 Générer rapport complet"):
            # Créer un rapport complet
            rapport = []
            rapport.append("RAPPORT D'ANALYSE - ÉTABLISSEMENTS SCOLAIRES MARRAKECH-ASAFI")
            rapport.append("=" * 70)
            rapport.append(f"Nombre total d'établissements: {df_filtered['NOM_ETABL'].nunique()}")
            rapport.append(f"Nombre total d'élèves: {df_filtered['id_eleve'].nunique()}")
            rapport.append(f"Nombre total de classes: {df_filtered['id_classe'].nunique()}")
            rapport.append("")
            
            # Statistiques par milieu
            rapport.append("RÉPARTITION PAR MILIEU:")
            rapport.append("-" * 25)
            for milieu in df_filtered['LL_MIL'].unique():
                data_milieu = df_filtered[df_filtered['LL_MIL'] == milieu]
                rapport.append(f"{milieu}:")
                rapport.append(f"  - Établissements: {data_milieu['NOM_ETABL'].nunique()}")
                rapport.append(f"  - Élèves: {data_milieu['id_eleve'].nunique()}")
                rapport.append(f"  - Classes: {data_milieu['id_classe'].nunique()}")
                rapport.append("")
            
            # Statistiques par type d'établissement
            rapport.append("RÉPARTITION PAR TYPE D'ÉTABLISSEMENT:")
            rapport.append("-" * 40)
            for type_etab in df_filtered['libformatFr'].unique():
                data_type = df_filtered[df_filtered['libformatFr'] == type_etab]
                rapport.append(f"{type_etab}:")
                rapport.append(f"  - Établissements: {data_type['NOM_ETABL'].nunique()}")
                rapport.append(f"  - Élèves: {data_type['id_eleve'].nunique()}")
                rapport.append("")
            
            # Statistiques par cycle
            rapport.append("RÉPARTITION PAR CYCLE:")
            rapport.append("-" * 25)
            for cycle in df_filtered['LL_CYCLE'].unique():
                data_cycle = df_filtered[df_filtered['LL_CYCLE'] == cycle]
                rapport.append(f"{cycle}:")
                rapport.append(f"  - Élèves: {data_cycle['id_eleve'].nunique()}")
                rapport.append("")
            
            rapport_text = "\n".join(rapport)
            st.sidebar.download_button(
                label="📄 Télécharger le rapport",
                data=rapport_text,
                file_name="rapport_analyse_etablissements.txt",
                mime="text/plain"
            )
        
        # Option pour télécharger les données filtrées
        if st.sidebar.button("📥 Télécharger données filtrées (Excel)"):
            df_export = df_filtered.copy()
            
            # Convertir en bytes pour le téléchargement
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, sheet_name='Données_Filtrées', index=False)
                
                # Ajouter une feuille avec les statistiques
                stats_summary = pd.DataFrame({
                    'Métrique': ['Établissements', 'Élèves', 'Classes', 'Communes', 'Types d\'Établ.'],
                    'Valeur': [
                        df_filtered['NOM_ETABL'].nunique(),
                        df_filtered['id_eleve'].nunique(),
                        df_filtered['id_classe'].nunique(),
                        df_filtered['ll_com'].nunique(),
                        df_filtered['libformatFr'].nunique()
                    ]
                })
                stats_summary.to_excel(writer, sheet_name='Statistiques', index=False)
            
            st.sidebar.download_button(
                label="📊 Télécharger Excel",
                data=output.getvalue(),
                file_name="donnees_etablissements_filtrees.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )  
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du fichier: {str(e)}")
        st.info("Vérifiez que votre fichier Excel contient toutes les colonnes requises.")
        
        # Afficher les détails de l'erreur pour le débogage
        with st.expander("🔍 Détails de l'erreur (pour débogage)"):
            st.text(str(e))
            import traceback
            st.text(traceback.format_exc())

else:
    st.info("👆 Veuillez télécharger votre fichier Excel pour commencer l'analyse.")
    
    # Affichage des colonnes attendues
    st.subheader("📋 Colonnes attendues dans votre fichier Excel:")
    colonnes_attendues = [
        "NOM_ETABL", "cd_com", "CD_MIL", "LL_MIL", "ll_com", 
        "nefstat", "id_eleve", "id_classe", "libformatFr", 
        "LL_CYCLE"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Colonnes principales :**")
        for i, col in enumerate(colonnes_attendues[:6], 1):
            st.write(f"{i}. **{col}**")
    
    with col2:
        st.markdown("**Colonnes additionnelles :**")
        for i, col in enumerate(colonnes_attendues[6:], 7):
            st.write(f"{i}. **{col}**")
    
    st.markdown("---")
    st.subheader("🎯 Fonctionnalités principales de l'application:")
    
    features = [
        "**📊 Vue d'ensemble**: Statistiques générales et répartition urbain/rural",
        "**🏫 Analyse Établissements**: Analyse par nom d'établissement, type et milieu",
        "**👥 Analyse Élèves**: Répartition des élèves par niveau et type d'établissement",
        "**📍 Analyse Provinciale**: Statistiques détaillées par province",
        "**📈 Visualisations Personnalisées**: Créez vos propres graphiques",
        "**🔍 Filtres Hiérarchiques**: Filtrage par Milieu → Commune → Établissement → Type → Cycle → Niveau",
        "**✏️ Renommage des Colonnes**: Personnalisez les noms des colonnes",
        "**💾 Export des Données**: Téléchargez les rapports et données filtrées"
    ]
    
    for feature in features:
        st.markdown(f"- {feature}")
    
    st.markdown("---")
    st.subheader("🔍 Guide d'utilisation des filtres hiérarchiques:")
    
    st.markdown("""
    1. **🌆 Milieu**: Sélectionnez Rural ou Urbain pour filtrer les établissements
    2. **🏘️ Commune**: Les communes disponibles dépendent du milieu sélectionné
    3. **🏫 Établissement**: Les établissements affichés correspondent à la commune choisie (par nom)
    4. **🏛️ Type d'Établissement**: Filtrez par type d'établissement (nouveau filtre)
    5. **🎓 Cycle**: Filtrez par cycle d'enseignement (Préscolaire, Primaire, Secondaire)
    6. **📚 Niveau**: Les niveaux disponibles dépendent du cycle sélectionné
    
    **Note**: Chaque filtre influence les options disponibles dans les filtres suivants pour maintenir la cohérence des données.
    """)
    
    st.markdown("---")
    st.subheader("🔄 Identification des élèves:")
    
    st.markdown("""
    L'application identifie automatiquement les élèves en comparant les colonnes :
    - **id_eleve** : Identifiant principal de l'élève
    
    **Critères de détection** :
    - Un élève est considéré comme identifié si `id_eleve` est renseigné
    - L'analyse des élèves est disponible par milieu, province, cycle, niveau et type d'établissement
    - Des statistiques détaillées et des visualisations sont générées automatiquement
    """)
    
    st.markdown("---")
    st.info("💡 **Conseil**: Assurez-vous que votre fichier Excel contient toutes les colonnes listées ci-dessus pour une analyse complète.")
    
    # Exemple de structure de données
    st.subheader("📋 Exemple de structure des données:")
    
    exemple_data = {
        'NOM_ETABL': ['École Primaire Al-Wifaq', 'Collège Ibn Battuta', 'École Maternelle Les Palmiers'],
        'LL_MIL': ['URBAIN', 'RURAL', 'URBAIN'],
        'll_com': ['MARRAKECH', 'ASAFI', 'MARRAKECH'],
        'typeEtab': ['École Primaire', 'Collège', 'École Maternelle'],
        'LL_CYCLE': ['PRIMAIRE', 'SECONDAIRE-COLLEGIAL', 'PRESCOLAIRE'],
        'libformatFr': ['1° Année Primaire Général', '1° Année Secondaire Collégial Général', 'PRESCOLAIRE'],
        'id_eleve': ['ELV001', 'ELV002', 'ELV003']
    }
    
    exemple_df = pd.DataFrame(exemple_data)
    st.dataframe(exemple_df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🆕 Nouveautés dans cette version:")
    
    nouveautes = [
        "**🏫 NOM_ETABL**: Affichage du nom complet des établissements au lieu des codes",
        "**🏛️ typeEtab**: Nouveau filtre et analyses par type d'établissement",
        "**📊 Visualisations enrichies**: Graphiques incluant les types d'établissements",
        "**🔍 Filtres améliorés**: Filtre hiérarchique par type d'établissement",
        "**📈 Analyses détaillées**: Statistiques croisées par type, milieu et cycle"
    ]
    
    for nouveaute in nouveautes:
        st.markdown(f"- {nouveaute}")
        
    st.markdown("---")
    st.markdown("**📞 Support**: Pour toute question sur l'utilisation de cette application, consultez la documentation ou contactez l'équipe technique.")
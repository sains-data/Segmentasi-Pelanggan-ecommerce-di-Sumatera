import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_segments
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import numpy as np

st.title("Segmentasi Pelanggan eCommerce Sumatera")

df = load_segments('/data/gold/customer_segments/')

# Asumsikan X adalah matrix fitur yang telah di-standarisasi
# dan features['Cluster'] sudah ada
labels = features['Cluster']
score = silhouette_score(X, labels)
print(f"Silhouette Score (KMeans, k=4): {score:.3f}")

# Silhouette analysis untuk k=2..8
scores = []
ks = range(2,9)
for k in ks:
    km = KMeans(n_clusters=k, random_state=42).fit(X)
    scores.append(silhouette_score(X, km.labels_))
plt.figure(figsize=(6,4))
plt.plot(ks, scores, marker='o')
plt.xlabel('Jumlah Cluster k')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Analysis untuk Memilih k')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# Scatter 3D RFM
fig3d = px.scatter_3d(df, x='Recency', y='Frequency', z='Monetary', color='cluster', title='3D Scatter RFM')
st.plotly_chart(fig3d)

# Boxplots R, F, M per cluster
for col in ['Recency','Frequency','Monetary']:
    fig = px.box(df, x='cluster', y=col, title=f'Distribusi {col} per Cluster')
    st.plotly_chart(fig)

# Barplot jumlah pelanggan
df_count = df['cluster'].value_counts().reset_index().rename(columns={'index':'cluster','cluster':'count'})
fig_bar = px.bar(df_count, x='cluster', y='count', title='Jumlah Pelanggan per Cluster')
st.plotly_chart(fig_bar)
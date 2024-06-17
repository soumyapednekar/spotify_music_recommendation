# -*- coding: utf-8 -*-
"""test3_603

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1o-vTEhlHuIe4xbFtwALmdtFeGaNNo4AH
"""

import numpy as np
import pandas as pd

import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from collections import defaultdict
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler, StandardScaler

import warnings
warnings.filterwarnings("ignore")

data= pd.read_csv('/content/data.csv')
artist_data = pd.read_csv('/content/data_by_artist.csv')
genre_data=pd.read_csv('/content/data_w_genres.csv')
year_data = pd.read_csv('/content/data_by_year.csv')

"""Data pre-processing"""

def remove_brackets(text):
    if isinstance(text, str):
        return text.replace("[", "").replace("]", "")
    else:
        return text

# Apply the function to the desired column
data['artists'] = data['artists'].apply(lambda x: remove_brackets(x))

# Display the updated DataFrame
print(data.head())

data['artists'] = data['artists'].str.replace('/', '').str.replace('?', '').str.replace(';', '').str.replace('©',' ').str.replace('¼','')
data.head()

# Commented out IPython magic to ensure Python compatibility.
import os
import numpy as np
import pandas as pd

import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
# %matplotlib inline

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
from collections import defaultdict
import difflib

import warnings
warnings.filterwarnings("ignore")

#Decade for years the song was hit
data['decade'] = data['year'].apply(lambda year : f'{(year//10)*10}s' )

sns.countplot(data['decade'],)

sound_features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'valence']
fig = px.line(year_data, x='year', y=sound_features,title='Trend of various sound features over decades',width=800,height=700)
fig.show()

fig = px.line(year_data, x='year', y='loudness',title='Trend of loudness over decades')
fig.show()



top10_genres = genre_data.nlargest(10, 'popularity')

fig = px.bar(top10_genres, x='genres', y=['valence', 'energy', 'danceability', 'acousticness'], barmode='group',
            title='Trend of various sound features over top 10 genres')
fig.show()

from wordcloud import WordCloud,STOPWORDS

stopwords = set(STOPWORDS)
comment_words = " ".join(genre_data['genres'])+" "
wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                max_words=40,
                min_font_size = 10).generate(comment_words)

plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
plt.title("Genres Wordcloud")
plt.show()

top10_popular_artists = artist_data.nlargest(10, 'popularity')
top10_most_song_produced_artists = artist_data.nlargest(10, 'count')

print('Top 10 Artists that produced most songs:')
top10_most_song_produced_artists[['count','artists']].sort_values('count',ascending=False)

print('Top 10 Artists that had most popularity score:')
top10_popular_artists[['popularity','artists']].sort_values('popularity',ascending=False)
print(top10_popular_artists['artists'])

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

cluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans(n_clusters=12))])
X = genre_data.select_dtypes(np.number)
cluster_pipeline.fit(X)
genre_data['cluster'] = cluster_pipeline.predict(X)

from sklearn.manifold import TSNE

tsne_pipeline = Pipeline([('scaler', StandardScaler()), ('tsne', TSNE(n_components=2, verbose=1))])
genre_embedding = tsne_pipeline.fit_transform(X) # returns np-array of coordinates(x,y) for each record after TSNE.
projection = pd.DataFrame(columns=['x', 'y'], data=genre_embedding)
projection['genres'] = genre_data['genres']
projection['cluster'] = genre_data['cluster']

fig = px.scatter(
    projection, x='x', y='y', color='cluster', hover_data=['x', 'y', 'genres'],title='Clusters of genres')
fig.show()

# Changes in Tempo Over the Years
fig = px.scatter(year_data, x='year', y='tempo', color='tempo', size='popularity',
                 title='Changes in Tempo Over the Years', labels={'tempo': 'Tempo --->', "year":"Years --->"})
fig.show()

song_cluster_pipeline = Pipeline([('scaler', StandardScaler()),
                                  ('kmeans', KMeans(n_clusters=25,
                                   verbose=False))
                                 ], verbose=False)

X = data.select_dtypes(np.number)
song_cluster_pipeline.fit(X)
song_cluster_labels = song_cluster_pipeline.predict(X)
data['cluster_label'] = song_cluster_labels

from sklearn.decomposition import PCA

pca_pipeline = Pipeline([('scaler', StandardScaler()), ('PCA', PCA(n_components=2))])
song_embedding = pca_pipeline.fit_transform(X)
projection = pd.DataFrame(columns=['x', 'y'], data=song_embedding)
projection['title'] = data['name']
projection['cluster'] = data['cluster_label']

fig = px.scatter(
    projection, x='x', y='y', color='cluster', hover_data=['x', 'y', 'title'],title='Clusters of songs')
fig.show()

"""**Music Recommendation**"""

# List of numerical columns to consider for similarity calculations
number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit', 'year',
               'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']

# Function to retrieve song data for a given song name
def get_song_data(name, data):
    try:
        return data[data['name'].str.lower() == name].iloc[0]
        return song_data
    except IndexError:
        return None

# Function to calculate the mean vector of a list of songs
def get_mean_vector(song_list, data):
    song_vectors = []
    for song in song_list:
        song_data = get_song_data(song['name'], data)
        if song_data is None:
            print('Warning: {} does not exist in the dataset'.format(song['name']))
            return None
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)

# Function to flatten a list of dictionaries into a single dictionary
def flatten_dict_list(dict_list):
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
    return flattened_dict
# Normalize the song data using Min-Max Scaler
min_max_scaler = MinMaxScaler()
normalized_data = min_max_scaler.fit_transform(data[number_cols])

# Standardize the normalized data using Standard Scaler
standard_scaler = StandardScaler()
scaled_normalized_data = standard_scaler.fit_transform(normalized_data)
# Function to recommend songs based on a list of seed songs
def recommend_songs(seed_songs, data, n_recommendations=10):
    metadata_cols = ['name', 'artists', 'year']
    song_center = get_mean_vector(seed_songs, data)

    # Return an empty list if song_center is missing
    if song_center is None:
        return []

    # Normalize the song center
    normalized_song_center = min_max_scaler.transform([song_center])

    # Standardize the normalized song center
    scaled_normalized_song_center = standard_scaler.transform(normalized_song_center)

    # Calculate Euclidean distances and get recommendations
    distances = cdist(scaled_normalized_song_center, scaled_normalized_data, 'euclidean')
    index = np.argsort(distances)[0]

    # Filter out seed songs and duplicates, then get the top n_recommendations
    rec_songs = []
    for i in index:
        song_name = data.iloc[i]['name']
        if song_name not in [song['name'] for song in seed_songs] and song_name not in [song['name'] for song in rec_songs]:
            rec_songs.append(data.iloc[i])
            if len(rec_songs) == n_recommendations:
                break

    return pd.DataFrame(rec_songs)[metadata_cols].to_dict(orient='records')
# List of seed songs (replace with your own seed songs)
seed_songs = [
    {'name': 'Paranoid'},
    {'name': 'Blinding Lights'},
    # Add more seed songs as needed
]
seed_songs = [{'name': name['name'].lower()} for name in seed_songs]

# Number of recommended songs
n_recommendations = 10

# Call the recommend_songs function
recommended_songs = recommend_songs(seed_songs, data, n_recommendations)

# Convert the recommended songs to a DataFrame
recommended_df = pd.DataFrame(recommended_songs)

# Print the recommended songs
for idx, song in enumerate(recommended_songs, start=1):
    print(f"{idx}. {song['name']} by {song['artists']} ({song['year']})")



"""MODEL"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from sklearn.utils import resample
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
# Load the data
df = pd.read_csv('/content/data.csv')

# Define the columns to be used for clustering and logistic regression
number_cols = ['danceability', 'duration_ms', 'tempo', 'popularity']  # Add or remove attributes as needed

# K-Means Clustering for Genre Classification
kmeans = KMeans(n_clusters=10)  # Specify the number of clusters
genre_labels = kmeans.fit_predict(df[number_cols])

# Logistic Regression for Recommendation based on Song Popularity
X = df[number_cols[:-1]]  # Features (excluding 'popularity')
y = df['popularity']  # Target variable

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df[number_cols], genre_labels, test_size=0.2, random_state=42)

# Upsampling the minority classes to address class imbalance
X_train_upsampled, y_train_upsampled = resample(X_train, y_train, replace=True, n_samples=X_train.shape[0], random_state=42)

# Logistic Regression Model
log_reg = LogisticRegression(max_iter=10000)
log_reg.fit(X_train_upsampled, y_train_upsampled)

# Classification Report
y_pred = log_reg.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))

# ROC Curve
y_prob = log_reg.predict_proba(X_test)[:, 1]  # Probability estimates of the positive class
num_classes = len(np.unique(y_test))
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(num_classes):
   fpr[i], tpr[i], _ = roc_curve(y_test == i, y_prob, pos_label=i)
   roc_auc[i] = auc(fpr[i], tpr[i])

# Compute micro-average ROC curve and ROC area if there are only 2 unique classes
if len(np.unique(y_test)) == 2:
   fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_prob.ravel())
   roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])


seed_songs = [{'name': 'Come As You Are', 'year':1991},
               {'name': 'Smells Like Teen Spirit', 'year': 1991},
               {'name': 'Lithium', 'year': 1992},
               {'name': 'All Apologies', 'year': 1993},
               {'name': 'Stay Away', 'year': 1993}
             ]

def get_song_data(song_name, data):
   return data[data['name'] == song_name][number_cols].iloc[0]

# Recommendation Function
def recommend_songs_with_log_reg(seed_songs, data, n_recommendations=10):
   # Extract features for seed songs
   seed_song_features = [get_song_data(song['name'], data) for song in seed_songs]
   seed_song_features = np.array(seed_song_features)

   # Predict popularity for seed songs
   popularity_prob = log_reg.predict_proba(seed_song_features)[:, 1]

   # Recommend songs based on popularity prediction
   recommended_songs = data.iloc[popularity_prob.argsort()[::-1][:n_recommendations]]
   return recommended_songs

# Call the updated recommendation function
recommended_songs_with_log_reg = recommend_songs_with_log_reg(seed_songs, df)

# Print the recommended songs
for idx, song in enumerate(recommended_songs_with_log_reg.iterrows(), start=1):
   print(f"{idx}. {song[1]['name']} by {song[1]['artists']} ({song[1]['year']})")

plt.figure(figsize=(8, 6))

# Plot ROC curve for each class that has positive samples
for i in range(2):
   if np.sum(y_test == i) > 0:  # Check if there are positive samples for this class
       plt.plot(fpr[i], tpr[i], lw=2, label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

# Plot the diagonal line
plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--')

# Set labels and title
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")

plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from sklearn.utils import resample
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
# Load the data
df = pd.read_csv('/content/data.csv')

# Define the columns to be used for clustering and logistic regression
number_cols = ['danceability', 'duration_ms', 'tempo', 'popularity','loudness','instrumentalness']  # Add or remove attributes as needed

# K-Means Clustering for Genre Classification
kmeans = KMeans(n_clusters=10)  # Specify the number of clusters
genre_labels = kmeans.fit_predict(df[number_cols])

# Logistic Regression for Recommendation based on Song Popularity
X = df[number_cols[:-1]]  # Features (excluding 'popularity')
y = df['popularity']  # Target variable

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df[number_cols], genre_labels, test_size=0.2, random_state=42)

# Upsampling the minority classes to address class imbalance
X_train_upsampled, y_train_upsampled = resample(X_train, y_train, replace=True, n_samples=X_train.shape[0], random_state=42)

# Logistic Regression Model
log_reg = LogisticRegression(max_iter=10000)
log_reg.fit(X_train_upsampled, y_train_upsampled)

# Classification Report
y_pred = log_reg.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))

# ROC Curve
y_prob = log_reg.predict_proba(X_test)[:, 1]  # Probability estimates of the positive class
num_classes = len(np.unique(y_test))
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(num_classes):
   fpr[i], tpr[i], _ = roc_curve(y_test == i, y_prob, pos_label=i)
   roc_auc[i] = auc(fpr[i], tpr[i])

# Compute micro-average ROC curve and ROC area if there are only 2 unique classes
if len(np.unique(y_test)) == 2:
   fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_prob.ravel())
   roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])


seed_songs = [{'name': 'Come As You Are', 'year':1991},
               {'name': 'Smells Like Teen Spirit', 'year': 1991},
               {'name': 'Lithium', 'year': 1992},
               {'name': 'All Apologies', 'year': 1993},
               {'name': 'Stay Away', 'year': 1993}
             ]

def get_song_data(song_name, data):
   return data[data['name'] == song_name][number_cols].iloc[0]

# Recommendation Function
def recommend_songs_with_log_reg(seed_songs, data, n_recommendations=10):
   # Extract features for seed songs
   seed_song_features = [get_song_data(song['name'], data) for song in seed_songs]
   seed_song_features = np.array(seed_song_features)

   # Predict popularity for seed songs
   popularity_prob = log_reg.predict_proba(seed_song_features)[:, 1]

   # Recommend songs based on popularity prediction
   recommended_songs = data.iloc[popularity_prob.argsort()[::-1][:n_recommendations]]
   return recommended_songs

# Call the updated recommendation function
recommended_songs_with_log_reg = recommend_songs_with_log_reg(seed_songs, df)

# Print the recommended songs
for idx, song in enumerate(recommended_songs_with_log_reg.iterrows(), start=1):
   print(f"{idx}. {song[1]['name']} by {song[1]['artists']} ({song[1]['year']})")

plt.figure(figsize=(8, 6))

# Plot ROC curve for each class that has positive samples
for i in range(2):
   if np.sum(y_test == i) > 0:  # Check if there are positive samples for this class
       plt.plot(fpr[i], tpr[i], lw=2, label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

# Plot the diagonal line
plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--')

# Set labels and title
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")

plt.show()

df.info()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

# Load the data
df = pd.read_csv('/content/data.csv')

# Define the columns to be used for logistic regression
number_cols = ['danceability', 'duration_ms', 'tempo', 'popularity']

# Create a binary target variable based on a popularity threshold
threshold = 50
df['popularity_binary'] = np.where(df['popularity'] >= threshold, 1, 0)

# Features (X) and Target (y)
X = df[number_cols[:-1]]  # Features (excluding 'popularity')
y = df['popularity_binary']  # Binary target variable

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Logistic Regression Model
log_reg = LogisticRegression(max_iter=10000)
log_reg.fit(X_train, y_train)

# Predict probabilities and compute ROC curve
y_prob = log_reg.predict_proba(X_test)[:, 1]  # Probability estimates of the positive class

# Compute ROC curve and ROC area
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve (Popularity Threshold = %d)' % threshold)
plt.legend(loc="lower right")
plt.show()

"""Elvauation metrics"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Load the dataset
df = pd.read_csv('/content/data.csv')

# Select features and target variable
features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness',
            'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo']
target = 'popularity'

# One-hot encode the target variable
y = pd.get_dummies(df[target])

# Map one-hot encoded vectors to class labels
class_labels = np.argmax(y.values, axis=1)  # Convert one-hot to class labels

# Split the data into training and testing sets
X = df[features]
X_train, X_test, y_train, y_test = train_test_split(X, class_labels, test_size=0.2, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Logistic Regression model
log_reg = LogisticRegression(max_iter=1000)
log_reg.fit(X_train_scaled, y_train)

# Predict probabilities for test set
y_score = log_reg.predict_proba(X_test_scaled)

# Calculate evaluation metrics
accuracy = accuracy_score(y_test, np.argmax(y_score, axis=1))
precision = precision_score(y_test, np.argmax(y_score, axis=1), average='weighted')
recall = recall_score(y_test, np.argmax(y_score, axis=1), average='weighted')
f1 = f1_score(y_test, np.argmax(y_score, axis=1), average='weighted')

# Check number of unique classes in y_true and adjust y_score accordingly
n_classes = len(np.unique(y_test))
if n_classes == 2:
    roc_auc = roc_auc_score(y_test, y_score[:, 1])  # For binary classification
else:
    roc_auc = roc_auc_score(pd.get_dummies(y_test), y_score, multi_class='ovr')

# Print evaluation metrics
print(f'Accuracy: {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1-score: {f1:.4f}')
print(f'ROC AUC: {roc_auc:.4f}')

# Example debugging
print("Length of axis 1:", len(data.columns))  # Print the length of axis 1
problematic_index = 94
print("Attempting to access index:", problematic_index)
# Code line causing the error

y_test.shape

y_score.shape

data.head()

data.info()

data['popularity'].max()
data['popularity'].min()

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Assuming 'data' is your DataFrame containing the dataset
# Define features and target variable
features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'loudness', 'speechiness', 'tempo']
target = 'popularity'

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2, random_state=42)

# Initialize and train the regression model
reg_model = LinearRegression()
reg_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = reg_model.predict(X_test)

# Calculate evaluation metrics
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)  # RMSE by taking the square root of MSE
r2 = r2_score(y_test, y_pred)

# Print or visualize the evaluation metrics
print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R-squared (R2) Score: {r2}")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

# Load the data
df = pd.read_csv('/content/data.csv')

# Define the columns to be used for logistic regression
number_cols = ['danceability', 'duration_ms', 'tempo', 'mode']

# Features (X) and Target (y)
X = df[number_cols[:-1]]  # Features (excluding 'mode')
y = df['mode']  # Binary target variable

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Logistic Regression Model
log_reg = LogisticRegression(max_iter=10000)
log_reg.fit(X_train, y_train)

# Predict probabilities and compute ROC curve
y_prob = log_reg.predict_proba(X_test)[:, 1]  # Probability estimates of the positive class

# Compute ROC curve and ROC area
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve for Mode Prediction')
plt.legend(loc="lower right")
plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
from sklearn.metrics import roc_curve, auc

# Load the data
df = pd.read_csv('/content/data.csv')

# Define features and target
features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'loudness', 'speechiness', 'tempo']
target = 'popularity'

# Define thresholds and create popularity classes
thresholds = [20, 40, 60, 80]
class_labels = ['low', 'moderate', 'high', 'very_high']

df['popularity_class'] = pd.cut(df[target], bins=[-np.inf] + thresholds + [np.inf], labels=class_labels)

# Features (X) and Target (y)
X = df[features]
y = df['popularity_class']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Random Forest Classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Initialize One-vs-One (OvO) and One-vs-Rest (OvR) classifiers
ovo_classifier = OneVsOneClassifier(rf_classifier)
ovr_classifier = OneVsRestClassifier(rf_classifier)

# Train OvO and OvR classifiers
ovo_classifier.fit(X_train, y_train)
ovr_classifier.fit(X_train, y_train)

# Predict probabilities for each class on the test set
y_probs_ovo = ovo_classifier.predict_proba(X_test)
y_probs_ovr = ovr_classifier.predict_proba(X_test)

# Compute ROC curve and ROC AUC for each class (OvO)
plt.figure(figsize=(10, 8))
for i in range(len(class_labels)):
    fpr, tpr, _ = roc_curve(y_test == class_labels[i], y_probs_ovo[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f'{class_labels[i]} OvO ROC curve (area = {roc_auc:.2f})')

# Compute ROC curve and ROC AUC for each class (OvR)
for i in range(len(class_labels)):
    fpr, tpr, _ = roc_curve(y_test == class_labels[i], y_probs_ovr[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, linestyle='--', label=f'{class_labels[i]} OvR ROC curve (area = {roc_auc:.2f})')

plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve for Popularity Classes (OvO vs OvR)')
plt.legend(loc="lower right")
plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
from sklearn.metrics import roc_curve, auc

# Load the data
df = pd.read_csv('/content/data.csv')

# Define features and target
features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'loudness', 'speechiness', 'tempo']
target = 'popularity'

# Define thresholds and create popularity classes
thresholds = [0, 20, 40, 60, 80, 100]
class_labels = ['very_low', 'low', 'moderate', 'high', 'very_high']

# Map popularity values to classes
df['popularity_class'] = pd.cut(df[target], bins=thresholds, labels=class_labels, include_lowest=True)

# Features (X) and Target (y)
X = df[features]
y = df['popularity_class']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Random Forest Classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Initialize One-vs-One (OvO) and One-vs-Rest (OvR) classifiers
ovo_classifier = OneVsOneClassifier(rf_classifier)
ovr_classifier = OneVsRestClassifier(rf_classifier)

# Train OvO and OvR classifiers
ovo_classifier.fit(X_train, y_train)
ovr_classifier.fit(X_train, y_train)

# Predict probabilities for each class on the test set
y_probs_ovo = ovo_classifier.predict_proba(X_test)
y_probs_ovr = ovr_classifier.predict_proba(X_test)

# Compute ROC curve and ROC AUC for each class (OvO)
plt.figure(figsize=(10, 8))
for i in range(len(class_labels)):
    fpr, tpr, _ = roc_curve(y_test == class_labels[i], y_probs_ovo[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f'{class_labels[i]} OvO ROC curve (area = {roc_auc:.2f})')

# Compute ROC curve and ROC AUC for each class (OvR)
for i in range(len(class_labels)):
    fpr, tpr, _ = roc_curve(y_test == class_labels[i], y_probs_ovr[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, linestyle='--', label=f'{class_labels[i]} OvR ROC curve (area = {roc_auc:.2f})')

plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve for Popularity Classes (OvO vs OvR)')
plt.legend(loc="lower right")
plt.show()

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load the data
df = pd.read_csv('/content/data.csv')  # Update the file path

# Define features and target
features = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms',
            'energy', 'explicit', 'instrumentalness', 'key', 'liveness',
            'loudness', 'mode', 'speechiness', 'tempo']
target = 'popularity'

# Features (X) and Target (y)
X = df[features]
y = df[target]

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Random Forest Classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the classifier
rf_classifier.fit(X_train, y_train)

# Make predictions
y_pred = rf_classifier.predict(X_test)

# Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f'Accuracy: {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1 Score: {f1:.4f}')

import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load the data
df = pd.read_csv('/content/data.csv')  # Update the file path

# Define features and target
features = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms',
            'energy', 'explicit', 'instrumentalness', 'key', 'liveness',
            'loudness', 'mode', 'speechiness', 'tempo']
target = 'popularity'

# Features (X) and Target (y)
X = df[features]
y = df[target]

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Random Forest Classifier
rf_classifier = RandomForestClassifier(random_state=42)

# Define hyperparameters to tune
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Initialize GridSearchCV
grid_search = GridSearchCV(estimator=rf_classifier, param_grid=param_grid,
                           scoring='accuracy', cv=3, verbose=2, n_jobs=-1)

# Perform grid search to find best hyperparameters
grid_search.fit(X_train, y_train)

# Get the best hyperparameters
best_params = grid_search.best_params_
print(f"Best Hyperparameters:\n{best_params}")

# Use the best model for predictions
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f'Accuracy: {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1 Score: {f1:.4f}')

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler

# Load the data
df = pd.read_csv('/content/data.csv')

# Define features
features = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms',
            'energy', 'explicit', 'instrumentalness', 'key', 'liveness',
            'loudness', 'mode', 'speechiness', 'tempo']

# Features (X)
X = df[features]

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Initialize KMeans clustering
kmeans = KMeans(n_clusters=5, random_state=42)  # Set the number of clusters as needed

# Fit the KMeans model
kmeans.fit(X_scaled)

# Get cluster labels and evaluate clustering metrics
cluster_labels = kmeans.labels_

# Silhouette Score
silhouette_avg = silhouette_score(X_scaled, cluster_labels)
print(f'Silhouette Score: {silhouette_avg:.4f}')

# Davies-Bouldin Index
db_index = davies_bouldin_score(X_scaled, cluster_labels)
print(f'Davies-Bouldin Index: {db_index:.4f}')

# Calinski-Harabasz Index
ch_index = calinski_harabasz_score(X_scaled, cluster_labels)
print(f'Calinski-Harabasz Index: {ch_index:.4f}')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Load the dataset
df = pd.read_csv('/content/data.csv')

# Select features and target variable
features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness',
            'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo']
target = 'popularity'

# Split the data into features and target variable
X = df[features]
y = df[target]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Define models
models = {
    "Random Forest": RandomForestClassifier(random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "Logistic Regression": LogisticRegression(random_state=42),
    "SVM": SVC(probability=True, random_state=42)
}

# Dictionary to store evaluation metrics for each model
results = {}

# Train and evaluate each model
for name, model in models.items():
    # Train model
    model.fit(X_train_scaled, y_train)

    # Predict probabilities for test set
    y_score = model.predict_proba(X_test_scaled)

    # One-hot encode the target variable
    y_test_encoded = pd.get_dummies(y_test)

    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, np.argmax(y_score, axis=1))
    precision = precision_score(y_test, np.argmax(y_score, axis=1), average='weighted', zero_division=0)
    recall = recall_score(y_test, np.argmax(y_score, axis=1), average='weighted', zero_division=0)
    f1 = f1_score(y_test, np.argmax(y_score, axis=1), average='weighted', zero_division=0)

    if len(np.unique(y_train)) == 2:  # Binary classification
        roc_auc = roc_auc_score(y_test_encoded, y_score[:, 1])
    else:  # Multiclass classification
        roc_auc = roc_auc_score(y_test_encoded, y_score, multi_class='ovr', average='macro')

    # Store results
    results[name] = {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1,
        "ROC AUC": roc_auc
    }

# Print results
for name, metrics in results.items():
    print(f"{name}:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    print()
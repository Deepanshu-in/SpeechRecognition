import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
from scipy.stats import pearsonr

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

class TEDTalksRecommendationSystem:
    def __init__(self):
        # Generate sample TED Talks dataset
        self.generate_dataset()
        
    def generate_dataset(self):
        """Generate a sample dataset of TED Talks"""
        speakers = [
            "Author 1",     # Education & Inspiration
            "Author 2",     # Leadership & Personal Growth
            "Author 3",     # Social Change & History
            "Author 4",     # Storytelling
            "Author 5",     # Personal Growth & Motivation
            "Author 6",     # Creativity & Communication
            "Author 7",     # Data Visualization & Leadership
            "Author 8",     # Social Change
            "Author 9",     # Personal Growth & Storytelling
            "Author 10"     # Social Change & Education
        ]

        topics = [
            "Education", 
            "Creativity", 
            "Vulnerability", 
            "Data Visualization", 
            "Leadership", 
            "Personal Growth", 
            "Storytelling", 
            "Motivation", 
            "History", 
            "Social Change"
        ]
        
        # Create synthetic dataset with more realistic date distribution
        import random
        np.random.seed(42)  # for reproducibility
        
        # More recent years with varying talk frequencies
        years = [2018, 2019, 2020, 2021, 2022, 2023]
        year_weights = [0.1, 0.15, 0.2, 0.2, 0.2, 0.15]
        
        # Create synthetic dataset
        data = {
            'title': [f"{speaker}'s Talk on {topic}" for speaker in speakers for topic in topics],
            'speaker': speakers * len(topics),
            'description': [
                f"A profound exploration of {topic} by {speaker}, challenging our understanding and inspiring change."
                for speaker in speakers for topic in topics
            ],
            'date': [f"{random.choices(years, weights=year_weights)[0]}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}" 
                     for _ in range(len(speakers) * len(topics))],
            'views': np.random.randint(10000, 1000000, len(speakers) * len(topics))
        }
        
        self.df = pd.DataFrame(data)
        
    def preprocess_data(self):
        """Handle missing values and prepare data"""
        # Check for missing values
        print("Missing Values:")
        print(self.df.isnull().sum())
        
        # Fill missing values if any
        self.df['description'] = self.df['description'].fillna('No description available')
        
    def visualize_talks_per_year(self):
        """Visualize number of TED Talks per year"""
        # Extract year from date
        self.df['year'] = pd.to_datetime(self.df['date']).dt.year
        
        # Count talks per year
        talks_per_year = self.df['year'].value_counts().sort_index()
        
        plt.figure(figsize=(12, 6))
        talks_per_year.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Number of TED Talks per Year', fontsize=15)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Number of Talks', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    def text_preprocessing(self):
        """Preprocess text data"""
        # Convert to lowercase
        self.df['processed_description'] = self.df['description'].str.lower()
        
        # Remove punctuation
        self.df['processed_description'] = self.df['processed_description'].apply(
            lambda x: x.translate(str.maketrans('', '', string.punctuation))
        )
        
        # Remove stop words
        stop_words = set(stopwords.words('english'))
        self.df['processed_description'] = self.df['processed_description'].apply(
            lambda x: ' '.join([word for word in x.split() if word not in stop_words])
        )
        
    def generate_word_cloud(self):
        """Generate word cloud from processed descriptions"""
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white'
        ).generate(' '.join(self.df['processed_description']))
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('TED Talks Description Word Cloud')
        plt.show()
        
    def create_recommendation_system(self, user_interests):
        """
        Create recommendation system using TF-IDF and Cosine Similarity
        
        :param user_interests: List of user's interest keywords
        :return: Recommended TED Talks
        """
        # TF-IDF Vectorization
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.df['processed_description'])
        
        # User interests vector
        user_vector = tfidf.transform([' '.join(user_interests)])
        
        # Compute cosine similarity
        cosine_sim = cosine_similarity(user_vector, tfidf_matrix)[0]
        
        # Compute Pearson correlation for additional similarity
        def pearson_similarity(vec1, vec2):
            try:
                return pearsonr(vec1, vec2)[0]
            except:
                return 0
        
        # Combine similarity scores
        combined_similarity = [
            (cosine_sim[i] + pearson_similarity(user_vector.toarray()[0], tfidf_matrix[i].toarray()[0])) / 2 
            for i in range(len(self.df))
        ]
        
        # Rank talks by similarity
        ranked_talks = sorted(
            enumerate(combined_similarity), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return top 5 recommended talks
        recommended_talks = [
            {
                'title': self.df.iloc[idx]['title'],
                'similarity_score': score
            }
            for idx, score in ranked_talks[:5]
        ]
        
        return recommended_talks
    
    def run_recommendation_system(self, user_interests):
        """Main method to run the entire recommendation system"""
        # Preprocess data
        self.preprocess_data()
        
        # Visualize talks per year
        self.visualize_talks_per_year()
        
        # Text preprocessing
        self.text_preprocessing()
        
        # Generate word cloud
        self.generate_word_cloud()
        
        # Get recommendations
        recommendations = self.create_recommendation_system(user_interests)
        
        print("\nRecommended TED Talks:")
        for talk in recommendations:
            print(f"Title: {talk['title']}")
            print(f"Similarity Score: {talk['similarity_score']:.4f}\n")

# Example usage
def main():
    # Initialize recommendation system
    recommender = TEDTalksRecommendationSystem()
    
    # Example user interests
    user_interests = ['education', 'creativity', 'leadership']
    
    # Run recommendation system
    recommender.run_recommendation_system(user_interests)

if __name__ == "__main__":
    main()